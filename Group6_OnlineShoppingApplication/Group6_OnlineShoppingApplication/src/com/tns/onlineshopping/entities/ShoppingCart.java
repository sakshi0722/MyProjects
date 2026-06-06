package com.tns.onlineshopping.entities;

import java.util.HashMap;
import java.util.Map;

public class ShoppingCart {
 private Customer customer;
 private Map<Product, Integer> items; // Product to quantity

 public ShoppingCart(Customer customer) {
     this.customer = customer;
     this.items = new HashMap<>();
 }

 // Getters
 public Customer getCustomer() { return customer; }
 public Map<Product, Integer> getItems() { return items; }

 public void addItem(Product product, int quantity) {
     items.put(product, items.getOrDefault(product, 0) + quantity);
     System.out.println(quantity + " of " + product.getName() + " added to cart.");
 }

 public void removeItem(Product product) {
     if (items.containsKey(product)) {
         items.remove(product);
         System.out.println(product.getName() + " removed from cart.");
     } else {
         System.out.println(product.getName() + " not found in cart.");
     }
 }

 public void updateItemQuantity(Product product, int newQuantity) {
     if (items.containsKey(product)) {
         if (newQuantity > 0) {
             items.put(product, newQuantity);
             System.out.println("Quantity of " + product.getName() + " updated to " + newQuantity);
         } else {
             removeItem(product);
         }
     } else {
         System.out.println(product.getName() + " not found in cart.");
     }
 }

 public void clearCart() {
     items.clear();
     System.out.println("Shopping cart cleared.");
 }

 @Override
 public String toString() {
     if (items.isEmpty()) {
         return "Shopping cart for " + customer.getUsername() + " is empty.";
     }
     StringBuilder sb = new StringBuilder();
     sb.append("Shopping Cart for ").append(customer.getUsername()).append(":\n");
     for (Map.Entry<Product, Integer> entry : items.entrySet()) {
         sb.append("  ").append(entry.getKey().getName()).append(" x ").append(entry.getValue()).append("\n");
     }
     return sb.toString();
 }
}
