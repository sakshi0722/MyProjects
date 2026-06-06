package com.tns.onlineshopping.entities;


public class Admin extends User {
 public Admin(String userId, String username, String email) {
     super(userId, username, email);
 }

 
 @Override
 public String toString() {
     return "Admin " + super.toString();
 }
}
