package com.tns.onlineshopping.entities;


public class ProductQuantityPair {
 private Product product;
 private int quantity;

 public ProductQuantityPair(Product product, int quantity) {
     this.product = product;
     this.quantity = quantity;
 }

 // Getters
 public Product getProduct() { return product; }
 public int getQuantity() { return quantity; }

 // Setters
 public void setQuantity(int quantity) { this.quantity = quantity; }

 @Override
 public String toString() {
     return "Product: " + product.getName() + ", Quantity: " + quantity;
 }
}
