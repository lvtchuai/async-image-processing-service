resource "aws_ecr_repository" "this" {
  for_each             = toset(var.names)
  name                 = each.value
  image_tag_mutability = "MUTABLE"
  force_delete         = true # cho destroy dù còn image (lab)
  image_scanning_configuration { scan_on_push = true }
}
