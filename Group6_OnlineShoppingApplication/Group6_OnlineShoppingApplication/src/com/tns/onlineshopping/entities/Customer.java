package com.tns.onlineshopping.entities;


import java.util.ArrayList;
import java.util.List;

public class Customer extends User {
 private String address;
 private ShoppingCart shoppingCart;
 private List<Order> orders;

 public Customer(String userId, String username, String email, String address) {
     super(userId, username, email);
     this.address = address;
     this.shoppingCart = new ShoppingCart(this); // One-to-one with ShoppingCart
     this.orders = new ArrayList<>(); // One-to-many with Order
 }

 // Getters
 public String getAddress() { return address; }
 public ShoppingCart getShoppingCart() { return shoppingCart; }
 public List<Order> getOrders() { return orders; }

 // Setters
 public void setAddress(String address) { this.address = address; }

 public void addOrder(Order order) {
     this.orders.add(order);
 }

 @Override
 public String toString() {
     return super.toString() + ", Address: " + address;
 }
}
