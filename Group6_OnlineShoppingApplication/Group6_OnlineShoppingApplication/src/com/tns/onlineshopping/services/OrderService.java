package com.tns.onlineshopping.services;

import com.tns.onlineshopping.entities.Order;
import com.tns.onlineshopping.entities.Product;
import com.tns.onlineshopping.entities.ProductQuantityPair;
import com.tns.onlineshopping.entities.Customer;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class OrderService {
 private Map<String, Order> orders; // orderId -> Order
 private ProductService productService; // To update stock quantities

 public OrderService(ProductService productService) {
     this.orders = new HashMap<>();
     this.productService = productService;
 }

 public Order placeOrder(Customer customer, Map<Product, Integer> itemsInCart) {
     List<ProductQuantityPair> orderProducts = new ArrayList<>();
     boolean stockAvailable = true;

     // Check stock first
     for (Map.Entry<Product, Integer> entry : itemsInCart.entrySet()) {
         Product product = entry.getKey();
         int quantity = entry.getValue();
         if (product.getStockQuantity() < quantity) {
             System.out.println("Insufficient stock for " + product.getName() + ". Available: " + product.getStockQuantity() + ", Requested: " + quantity);
             stockAvailable = false;
             break;
         }
         orderProducts.add(new ProductQuantityPair(product, quantity));
     }

     if (!stockAvailable) {
         System.out.println("Order could not be placed due to insufficient stock.");
         return null;
     }

     // Decrease stock and create order
     for (ProductQuantityPair pqp : orderProducts) {
         pqp.getProduct().decreaseStock(pqp.getQuantity());
     }

     Order order = new Order(customer, orderProducts);
     orders.put(order.getOrderId(), order);
     customer.addOrder(order); // Add order to customer's list
     System.out.println("Order placed successfully! Order ID: " + order.getOrderId());
     return order;
 }

 public Order getOrderById(String orderId) {
     return orders.get(orderId);
 }

 public void updateOrderStatus(String orderId, String newStatus) {
     Order order = orders.get(orderId);
     if (order != null) {
         String oldStatus = order.getStatus();
         order.setStatus(newStatus);
         System.out.println("Order " + orderId + " status updated from " + oldStatus + " to " + newStatus);

         // If order is cancelled, return stock
         if (newStatus.equalsIgnoreCase("Cancelled") && !oldStatus.equalsIgnoreCase("Cancelled")) {
             for (ProductQuantityPair p : order.getProducts()) {
                 p.getProduct().increaseStock(p.getQuantity());
                 System.out.println("Stock for " + p.getProduct().getName() + " increased by " + p.getQuantity() + " due to cancellation.");
             }
         }
     } else {
         System.out.println("Order not found.");
     }
 }

 public void listOrdersForCustomer(String customerId) {
     boolean found = false;
     System.out.println("Orders for Customer ID: " + customerId);
     for (Order order : orders.values()) {
         if (order.getCustomer().getUserId().equals(customerId)) {
             System.out.println(order);
             found = true;
         }
     }
     if (!found) {
         System.out.println("No orders found for this customer.");
     }
 }

 public void listAllOrders() {
     if (orders.isEmpty()) {
         System.out.println("No orders placed yet.");
         return;
     }
     System.out.println("All Orders:");
     for (Order order : orders.values()) {
         System.out.println(order);
     }
 }
}
