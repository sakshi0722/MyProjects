package com.tns.onlineshopping.services;

import com.tns.onlineshopping.entities.Product;
import java.util.HashMap;
import java.util.Map;

public class ProductService {
 private Map<String, Product> products; // productId -> Product

 public ProductService() {
     this.products = new HashMap<>();
 }

 public void addProduct(Product product) {
     if (products.containsKey(product.getProductId())) {
         System.out.println("Product with ID " + product.getProductId() + " already exists.");
     } else {
         products.put(product.getProductId(), product);
         System.out.println("Product added successfully!");
     }
 }

 public Product getProductById(String productId) {
     return products.get(productId);
 }

 public void updateProduct(String productId, String name, double price, int stockQuantity) {
     Product product = products.get(productId);
     if (product != null) {
         product.setName(name);
         product.setPrice(price);
         product.setStockQuantity(stockQuantity);
         System.out.println("Product updated successfully!");
     } else {
         System.out.println("Product not found.");
     }
 }

 public void removeProduct(String productId) {
     if (products.remove(productId) != null) {
         System.out.println("Product removed successfully!");
     } else {
         System.out.println("Product not found.");
     }
 }

 public void listAllProducts() {
     if (products.isEmpty()) {
         System.out.println("No products available.");
         return;
     }
     System.out.println("Products:");
     for (Product product : products.values()) {
         System.out.println(product);
     }
 }
}
