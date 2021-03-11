from django.db import models


# Create your models here.
class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=500)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=500)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='shop/images', default="")
    featured = models.BooleanField(null=False, blank=True)

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    user_id = models.AutoField
    user_name = models.CharField(max_length=50)
    user_email = models.CharField(max_length=50, default="")
    user_desc = models.CharField(max_length=50, default="")
    user_phn = models.IntegerField(default=0)

    def __str__(self):
        return self.user_name + "                 " + self.user_email


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000, default="")
    amount=models.IntegerField(default=0)
    name = models.CharField(max_length=90, default="")
    email = models.CharField(max_length=111, default="")
    address = models.CharField(max_length=111, default="")
    city = models.CharField(max_length=111, default="")
    state = models.CharField(max_length=111, default="")
    zip_code = models.CharField(max_length=111, default="")
    phone = models.CharField(max_length=111, default="")


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:35] + "               order-id" + str(self.order_id) + " " + str(self.timestamp)
