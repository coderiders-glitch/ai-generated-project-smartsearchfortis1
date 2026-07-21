resource "aws_opensearch_domain" "main" {
  domain_name            = local.app_name
  engine_version         = "OpenSearch_2.11"
  cluster_config {
    instance_type            = var.opensearch_instance_type
    instance_count           = var.opensearch_instance_count
    dedicated_master_enabled = true
    dedicated_master_type    = "t3.small.opensearch"
    dedicated_master_count   = 3
    zone_awareness_enabled   = true
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = var.opensearch_ebs_volume_size
  }

  vpc_options {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.opensearch.id]
  }

  node_to_node_encryption {
    enabled = true
  }

  encryption_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "admin"
      master_user_password = random_password.opensearch_password.result
    }
  }

  log_publishing_options {
    cloudwatch_log_group_arn = "${aws_cloudwatch_log_group.opensearch_app_logs.arn}:*"
    log_type                 = "ES_APPLICATION_LOGS"
    enabled                  = true
  }

  log_publishing_options {
    cloudwatch_log_group_arn = "${aws_cloudwatch_log_group.opensearch_index_logs.arn}:*"
    log_type                 = "INDEX_SLOW_LOGS"
    enabled                  = true
  }

  tags = local.common_tags
}

resource "aws_security_group" "opensearch" {
  name        = "${local.app_name}-opensearch-sg"
  description = "Security group for OpenSearch"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "opensearch_app_logs" {
  name              = "/aws/opensearch/${local.app_name}/app-logs"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "opensearch_index_logs" {
  name              = "/aws/opensearch/${local.app_name}/index-logs"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

resource "random_password" "opensearch_password" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret" "opensearch_password" {
  name                    = "${local.app_name}/opensearch/password"
  recovery_window_in_days = 7

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "opensearch_password" {
  secret_id     = aws_secretsmanager_secret.opensearch_password.id
  secret_string = random_password.opensearch_password.result
}