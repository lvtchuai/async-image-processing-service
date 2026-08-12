
resource "aws_security_group" "this" {
  name   = "${var.broker_name}-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 5671
    to_port     = 5671
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  } # AMQPS (TLS)

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  } # management HTTPS (KEDA)

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_mq_broker" "this" {
  broker_name         = var.broker_name
  engine_type                = "RabbitMQ"
  engine_version             = "3.13"
  auto_minor_version_upgrade = true
  host_instance_type         = "mq.m5.large" # RabbitMQ ở region này không có t3.micro; m5.large là nhỏ nhất
  deployment_mode     = "SINGLE_INSTANCE"
  publicly_accessible = false
  subnet_ids          = [var.subnet_ids[0]] # single instance = 1 subnet
  security_groups     = [aws_security_group.this.id]
  user {
    username = var.username
    password = var.password
  }
}

