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
  }
  backend "s3" {
    bucket                      = "rf-tofu-state"
    key                         = "doyoulikeit.tfstate"
    profile = "scaleway"
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


output "registry_endpoint" {
  value = scaleway_container_namespace.this.registry_endpoint
}

resource scaleway_container_namespace this {
    name = "doyoulikeit"
    description = "test container"
    region = "nl-ams"
}

resource scaleway_container this {
    name = "doyoulikeit"
    region = "nl-ams"
    namespace_id = scaleway_container_namespace.this.id
    registry_image = "${scaleway_container_namespace.this.registry_endpoint}/doyoulikeit:latest"
    privacy = "private"
    protocol = "http1"

    secret_environment_variables = {
      "DATABASE_URL" = neon_endpoint.this.host
    }
}

provider "neon" {}

resource "neon_project" "this" {
  name = "doyoulikeit"
}

resource "neon_branch" "main" {
  project_id = neon_project.this.id
  name       = "main"
}

resource "neon_endpoint" "this" {
  branch_id  = neon_branch.main.id
  project_id = neon_project.this.id
}

resource "neon_role" "owner" {
  branch_id  = neon_branch.main.id
  name       = "neondb_owner"
  project_id = neon_project.this.id
}

resource "neon_database" "this" {
  branch_id  = neon_branch.main.id
  name       = "neondb"
  owner_name = "neondb_owner"
  project_id = neon_project.this.id
}

resource "scaleway_inference_deployment" "deployment" {
  name = "doyoulikeit"
  node_type = "L4"
  model_name = "deepseek/deepseek-r1-distill-llama-8b"
  public_endpoint {
    is_enabled = true
  }
  accept_eula = true
}

import {
  to = neon_project.this
  id = "broad-wind-83397190"
}

import {
  to = neon_branch.main
  id = "br-restless-cell-ab98yu4t"
}

import {
  to = neon_endpoint.this
  id = "ep-shrill-rain-ab4tv8oe"
}

import {
  to = neon_role.owner
  id = "${neon_project.this.id}/${neon_branch.main.id}/neondb_owner"
}

import {
  to = neon_database.this
  id = "${neon_project.this.id}/${neon_branch.main.id}/neondb"
}
