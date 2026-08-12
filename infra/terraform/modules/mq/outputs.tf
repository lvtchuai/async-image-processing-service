output "amqps_endpoint" {
  value = aws_mq_broker.this.instances[0].endpoints[0]
} # amqps://...:5671

output "console_url" {
  value = aws_mq_broker.this.instances[0].console_url
}