package com.tns.onlineshopping.entities;

//Product.java
public class Product {
 private String productId;
 private String name;
 private double price;
 private int stockQuantity;

 public Product(String productId, String name, double price, int stockQuantity) {
     this.productId = productId;
     this.name = name;
     this.price = price;
     this.stockQuantity = stockQuantity;
 }

 // Getters
 public String getProductId() { return productId; }
 public String getName() { return name; }
 public double getPrice() { return price; }
 public int getStockQuantity() { return stockQuantity; }

 // Setters
 public void setName(String name) { this.name = name; }
 public void setPrice(double price) { this.price = price; }
 public void setStockQuantity(int stockQuantity) { this.stockQuantity = stockQuantity; }

 public void decreaseStock(int quantity) {
     if (this.stockQuantity >= quantity) {
         this.stockQuantity -= quantity;
     } else {
         System.out.println("Not enough stock for " + name);
     }
 }

 public void increaseStock(int quantity) {
     this.stockQuantity += quantity;
 }

 @Override
 public String toString() {
     return "Product [productId=" + productId + ", name=" + name + ", price=" + price + ", stockQuantity=" + stockQuantity + "]";
 }
}
