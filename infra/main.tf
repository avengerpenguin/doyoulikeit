terraform {
  required_version = ">= 1.9.0"
  required_providers {
    neon = {
      source  = "kislerdm/neon"
      version = ">= 0.2.2"
    }
    scaleway = {
      source = "scaleway/scaleway"
    }
    auth0 = {
      source  = "auth0/auth0"
      version = ">= 1.0.0" # Refer to docs for latest version
    }
  }
  backend "s3" {
    bucket                      = "rf-tofu-state"
    key                         = "doyoulikeit.tfstate"
    profile                     = "scaleway"
    region                      = "nl-ams"
    endpoint                    = "https://s3.nl-ams.scw.cloud"
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
  }
}

provider "scaleway" {
  region = "nl-ams"
}

provider "auth0" {}

provider "neon" {}

locals {
  auth0_client_id = "OyKMhFXN7AScYf1v6yxrFyjbTzoXQihZ"
}

output "registry_endpoint" {
  value = scaleway_container_namespace.this.registry_endpoint
}

output "url" {
  value = scaleway_container.this.domain_name
}

resource "scaleway_container_namespace" "this" {
  name        = "doyoulikeit"
  description = "test container"
  region      = "nl-ams"
}

resource "random_password" "auth0_key" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "scaleway_container" "this" {
  name           = "doyoulikeit"
  region         = "nl-ams"
  namespace_id   = scaleway_container_namespace.this.id
  registry_image = "${scaleway_container_namespace.this.registry_endpoint}/doyoulikeit:latest"
  privacy        = "public"
  memory_limit   = 128
  cpu_limit      = 70
  max_scale      = 1
  min_scale      = 0
  http_option    = "redirected"

  secret_environment_variables = {
    "DATABASE_URL"        = "postgresql://${neon_project.this.database_user}:${neon_project.this.database_password}@${neon_project.this.database_host_pooler}/${neon_project.this.database_name}?sslmode=require"
    "AUTH0_CLIENT_ID"     = local.auth0_client_id
    "AUTH0_CLIENT_SECRET" = data.auth0_client.this.client_secret
    "AUTH0_DOMAIN"        = "dev-zy4wj5zc3ka4savt.uk.auth0.com"
    "SECRET_KEY"          = random_password.auth0_key.result
  }
}



resource "neon_project" "this" {
  name      = "doyoulikeit"
  region_id = "aws-eu-west-2"
}


output "database_uri" {
  value     = "postgresql://${neon_project.this.database_user}:${neon_project.this.database_password}@${neon_project.this.database_host_pooler}/${neon_project.this.database_name}?sslmode=require"
  sensitive = true
}


resource "auth0_client" "this" {
  name            = "doyoulikeit"
  app_type        = "regular_web"
  callbacks       = ["http://localhost:8080/callback", "https://${scaleway_container.this.domain_name}/callback"]
  oidc_conformant = true
  depends_on      = [scaleway_container.this]
}


data "auth0_client" "this" {
  client_id = local.auth0_client_id
}


import {
  to = auth0_client.this
  id = local.auth0_client_id
}
