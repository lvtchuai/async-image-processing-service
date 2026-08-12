output "configure_kubectl" {
  value = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}"
}
output "ecr_urls"  { 
    value = module.ecr.repository_urls 
}
output "s3_bucket" { 
    value = module.s3.bucket_name 
}
output "rds_host"  { 
    value = module.rds.host 
}
output "mq_amqps"  { 
    value = module.mq.amqps_endpoint 
}   # amqps://...:5671
output "mq_console"{ 
    value = module.mq.console_url
}