package com.tns.onlineshopping.entities;

import java.util.ArrayList;
import java.util.List;

public class Order {
 private static int nextOrderId = 1;
 private String orderId;
 private Customer customer;
 private List<ProductQuantityPair> products;
 private String status; // e.g., "Pending", "Completed", "Delivered", "Cancelled"

 public Order(Customer customer, List<ProductQuantityPair> products) {
     this.orderId = String.valueOf(nextOrderId++);
     this.customer = customer;
     this.products = new ArrayList<>(products); // Deep copy to avoid external modification
     this.status = "Pending"; // Default status
 }

 // Getters
 public String getOrderId() { return orderId; }
 public Customer getCustomer() { return customer; }
 public List<ProductQuantityPair> getProducts() { return products; }
 public String getStatus() { return status; }

 // Setter
 public void setStatus(String status) { this.status = status; }

 @Override
 public String toString() {
     StringBuilder sb = new StringBuilder();
     sb.append("Order ID: ").append(orderId);
     sb.append(", Customer: ").append(customer.getUsername());
     sb.append(", Status: ").append(status);
     sb.append("\nProducts:");
     for (ProductQuantityPair p : products) {
         sb.append("\n  ").append(p.toString());
     }
     return sb.toString();
 }
}
