{ config, lib, pkgs, ... }:
let
  domain = "idp.localhost";
  port = 8443;

  certs =
    pkgs.runCommand "kanidm-self-signed-certs"
      {
        nativeBuildInputs = [ pkgs.openssl ];
      }
      ''
        mkdir -p $out

        # Generate CA private key
        openssl genrsa -out $out/ca.key 4096

        # Generate CA certificate
        openssl req -x509 -new -nodes \
          -key $out/ca.key \
          -sha256 \
          -days 3650 \
          -out $out/ca.crt \
          -subj "/CN=aoidc-test-ca/O=aoidc-test"

        # Generate server private key
        openssl genrsa -out $out/server.key 4096

        # Generate server CSR
        openssl req -new \
          -key $out/server.key \
          -out $out/server.csr \
          -subj "/CN=${domain}/O=aoidc-test"

        # Create extensions file for SAN
        cat > $out/ext.cnf <<EOF
        authorityKeyIdentifier=keyid,issuer
        basicConstraints=CA:FALSE
        keyUsage = digitalSignature, keyEncipherment
        extendedKeyUsage = serverAuth
        subjectAltName = @alt_names

        [alt_names]
        DNS.1 = ${domain}
        DNS.2 = localhost
        IP.1 = 127.0.0.1
        EOF

        # Sign server certificate with CA
        openssl x509 -req \
          -in $out/server.csr \
          -CA $out/ca.crt \
          -CAkey $out/ca.key \
          -CAcreateserial \
          -out $out/server.crt \
          -days 365 \
          -sha256 \
          -extfile $out/ext.cnf

        # Create certificate chain (server cert + CA cert)
        cat $out/server.crt $out/ca.crt > $out/chain.pem
      '';
in
{
  imports = lib.lists.flatten (with lib.r.modules; [ ]);

  security.pki.certificateFiles = [ "${certs}/ca.crt" ];

  microvm.forwardPorts = [
    {
      from = "host";
      host.port = port;
      guest.port = port;
    }
  ];

  environment.shellAliases = {
    "juk" = "journalctl -u kanidm";
    "klogin_idm" = "kanidm login -D idm_admin";
    "klogin_admin" = "kanidm login -D admin";
  };

  services.kanidm = {
    package = pkgs.kanidm_1_8.withSecretProvisioning;

    enableClient = true;
    clientSettings.uri = "https://${domain}:${toString port}";

    enableServer = true;

    provision = {
      enable = true;

      idmAdminPasswordFile = pkgs.writeText "kanidm-idm-admin-pw" "1";
      adminPasswordFile = pkgs.writeText "kanidm-admin-pw" "1";

      groups.aoidc_users = {
        present = true;
        members = [
          # "admin"
        ];
      };

      persons = {
        # admin = {
        #   present = true;
        #   displayName = "Admin";
        # };

        rubikoid = {
          present = true;
          displayName = "Rubikoid";
          legalName = "R R R";
          mailAddresses = [
            "rubikoid@localhost"
            "rubikoid@rubikoid.ru"
          ];
          groups = [
            "aoidc_users"
          ];
          # pw = 8fcg4i3tc345i
          # totp...
        };
      };

      systems.oauth2.aoidc = {
        present = true;

        displayName = "aOIDC Testing App";
        basicSecretFile = pkgs.writeText "aoidc-secret" "1337";

        originUrl = "http://127.0.0.1:9999";
        originLanding = "http://127.0.0.1:9999/wtf";
        enableLocalhostRedirects = true;

        public = false;
        allowInsecureClientDisablePkce = true;

        scopeMaps = {
          aoidc_users = [
            "email"
            "profile"
            "openid"
          ];
        };
      };
    };

    serverSettings = {
      tls_chain = "${certs}/chain.pem";
      tls_key = "${certs}/server.key";

      role = "WriteReplica";
      inherit domain;
      origin = "https://${domain}:${toString port}";
      log_level = "debug";

      bindaddress = "[::]:${toString port}";
    };
  };

  systemd.services.kanidm-postinit = {
    wantedBy = [ "multi-user.target" ];
    after = [
      "network-online.target"
      "kanidm.service"
    ];
    requires = [ "kanidm.service" ];

    script = ''
      #!${pkgs.bash}/bin/bash
      set -euo pipefail

      # Wait for the kanidm server to come online
      count=0
      while ! ${lib.getExe pkgs.curl} -L --silent --max-time 1 --connect-timeout 1 --fail \
        ${config.services.kanidm.provision.instanceUrl} >/dev/null
      do
        sleep 1
        if [[ "$count" -eq 30 ]]; then
          echo "Tried for at least 30 seconds, giving up..."
          exit 1
        fi
        count=$((++count))
      done

      ${config.services.kanidm.package}/bin/kanidm login -D idm_admin --password "1"
      ${config.services.kanidm.package}/bin/kanidm group add-members aoidc_users admin
      ${config.services.kanidm.package}/bin/kanidm system oauth2 add-redirect-url aoidc http://127.0.0.1:9999/docs/oauth2-redirect
    '';

    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = "yes";
      TimeoutStartSec = "0";
    };
  };
}
