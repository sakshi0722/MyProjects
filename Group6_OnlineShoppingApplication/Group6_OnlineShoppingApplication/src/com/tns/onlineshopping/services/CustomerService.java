package com.tns.onlineshopping.services;

import com.tns.onlineshopping.entities.Customer;
import java.util.HashMap;
import java.util.Map;

public class CustomerService {
 private Map<String, Customer> customers; // userId -> Customer

 public CustomerService() {
     this.customers = new HashMap<>();
 }

 public void addCustomer(Customer customer) {
     if (customers.containsKey(customer.getUserId())) {
         System.out.println("Customer with ID " + customer.getUserId() + " already exists.");
     } else {
         customers.put(customer.getUserId(), customer);
         System.out.println("Customer created successfully!");
     }
 }

 public Customer getCustomerById(String userId) {
     return customers.get(userId);
 }

 public void listAllCustomers() {
     if (customers.isEmpty()) {
         System.out.println("No customers available.");
         return;
     }
     System.out.println("Customers:");
     for (Customer customer : customers.values()) {
         System.out.println(customer);
     }
 }
}

