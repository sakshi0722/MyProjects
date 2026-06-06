package com.tns.onlineshopping.services;

import com.tns.onlineshopping.entities.Admin;
import com.tns.onlineshopping.entities.Product;

import java.util.HashMap;
import java.util.Map;

public class AdminServices {
 private Map<String, Admin> admins; // userId -> Admin
 private ProductService productService; // AdminService manages products

 public AdminServices(ProductService productService) {
     this.admins = new HashMap<>();
     this.productService = productService;
 }

 public void addAdmin(Admin admin) {
     if (admins.containsKey(admin.getUserId())) {
         System.out.println("Admin with ID " + admin.getUserId() + " already exists.");
     } else {
         admins.put(admin.getUserId(), admin);
         System.out.println("Admin created successfully!");
     }
 }

 public Admin getAdminById(String userId) {
     return admins.get(userId);
 }

 public void listAllAdmins() {
     if (admins.isEmpty()) {
         System.out.println("No admins available.");
         return;
     }
     System.out.println("Admins:");
     for (Admin admin : admins.values()) {
         System.out.println(admin);
     }
 }

 // Product management functionalities delegated to ProductService
 public void addProduct(String productId, String name, double price, int stockQuantity) {
     productService.addProduct(new Product(productId, name, price, stockQuantity));
 }

 public void removeProduct(String productId) {
     productService.removeProduct(productId);
 }

 public void updateProduct(String productId, String name, double price, int stockQuantity) {
     productService.updateProduct(productId, name, price, stockQuantity);
 }

 public void viewProducts() {
     productService.listAllProducts();
 }
}
