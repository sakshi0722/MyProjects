
package com.tns.onlineshopping.application;

import com.tns.onlineshopping.entities.*;
import com.tns.onlineshopping.services.*;

//import java.util.InputMismatchException;
//import java.util.List;
//import java.util.Map;
//import java.util.Scanner;

import java.util.*;

public class onlineShopping {
	private static ProductService productService = new ProductService();
    private static CustomerService customerService = new CustomerService();
    private static AdminServices adminService = new AdminServices(productService);
    private static OrderService orderService = new OrderService(productService);
    private static Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        // Initial data for testing
        adminService.addAdmin(new Admin("A001", "SuperAdmin", "admin@shop.com"));
        productService.addProduct(new Product("P101", "T-Shirt", 560.0, 100));
        productService.addProduct(new Product("P102", "Trouser", 1400.0, 50));
        productService.addProduct(new Product("P103", "Sneakers", 2500.0, 30));

        int choice;
        do {
            System.out.println("\n--- Main Menu ---");
            System.out.println("1. Admin Menu");
            System.out.println("2. Customer Menu");
            System.out.println("3. Exit");
            System.out.print("Choose an option: ");
            choice = getIntInput();

            switch (choice) {
                case 1:
                    adminMenu();
                    break;
                case 2:
                    customerMenu();
                    break;
                case 3:
                    System.out.println("Exiting...");
                    break;
                default:
                    System.out.println("Invalid option. Please try again.");
            }
        } while (choice != 3);

        scanner.close();
    }

    private static int getIntInput() {
        while (!scanner.hasNextInt()) {
            System.out.println("Invalid input. Please enter a number.");
            scanner.next(); // consume the invalid input
            System.out.print("Choose an option: ");
        }
        int input = scanner.nextInt();
        scanner.nextLine(); // consume newline
        return input;
    }

    private static double getDoubleInput() {
        while (!scanner.hasNextDouble()) {
            System.out.println("Invalid input. Please enter a number.");
            scanner.next(); // consume the invalid input
            System.out.print("Enter price: ");
        }
        double input = scanner.nextDouble();
        scanner.nextLine(); // consume newline
        return input;
    }

    private static void adminMenu() {
        int choice;
        do {
            System.out.println("\n--- Admin Menu ---");
            System.out.println("1. Add Product");
            System.out.println("2. Remove Product");
            System.out.println("3. View Products");
            System.out.println("4. Create Admin");
            System.out.println("5. View Admins");
            System.out.println("6. Update Order Status");
            System.out.println("7. View Orders");
            System.out.println("8. Return to Main Menu");
            System.out.print("Choose an option: ");
            choice = getIntInput();

            switch (choice) {
                case 1:
                    System.out.print("Enter Product ID: ");
                    String pId = scanner.nextLine();
                    System.out.print("Enter Product Name: ");
                    String pName = scanner.nextLine();
                    System.out.print("Enter Product Price: ");
                    double pPrice = getDoubleInput();
                    System.out.print("Enter Stock Quantity: ");
                    int pStock = getIntInput();
                    adminService.addProduct(pId, pName, pPrice, pStock);
                    break;
                case 2:
                    System.out.print("Enter Product ID to remove: ");
                    String removePId = scanner.nextLine();
                    adminService.removeProduct(removePId);
                    break;
                case 3:
                    adminService.viewProducts();
                    break;
                case 4:
                    System.out.print("Enter Admin User ID: ");
                    String adminId = scanner.nextLine();
                    System.out.print("Enter Admin Username: ");
                    String adminUsername = scanner.nextLine();
                    System.out.print("Enter Admin Email: ");
                    String adminEmail = scanner.nextLine();
                    adminService.addAdmin(new Admin(adminId, adminUsername, adminEmail));
                    break;
                case 5:
                    adminService.listAllAdmins();
                    break;
                case 6:
                    System.out.print("Enter Order ID to update status: ");
                    String orderId = scanner.nextLine();
                    System.out.print("Enter new status (Completed/Delivered/Cancelled): ");
                    String newStatus = scanner.nextLine();
                    orderService.updateOrderStatus(orderId, newStatus);
                    break;
                case 7:
                    orderService.listAllOrders();
                    break;
                case 8:
                    System.out.println("Exiting Admin Menu...");
                    break;
                default:
                    System.out.println("Invalid option. Please try again.");
            }
        } while (choice != 8);
    }

    private static void customerMenu() {
        int choice;
        do {
            System.out.println("\n--- Customer Menu ---");
            System.out.println("1. Create Customer");
            System.out.println("2. View Customers");
            System.out.println("3. Place Order");
            System.out.println("4. View My Orders");
            System.out.println("5. View Products");
            System.out.println("6. Return to Main Menu");
            System.out.print("Choose an option: ");
            choice = getIntInput();

            switch (choice) {
                case 1:
                    System.out.print("Enter User ID: ");
                    String cId = scanner.nextLine();
                    System.out.print("Enter Username: ");
                    String cUsername = scanner.nextLine();
                    System.out.print("Enter Email: ");
                    String cEmail = scanner.nextLine();
                    System.out.print("Enter Address: ");
                    String cAddress = scanner.nextLine();
                    customerService.addCustomer(new Customer(cId, cUsername, cEmail, cAddress));
                    break;
                case 2:
                    customerService.listAllCustomers();
                    break;
                case 3:
                    System.out.print("Enter Customer ID: ");
                    String customerIdForOrder = scanner.nextLine();
                    Customer customer = customerService.getCustomerById(customerIdForOrder);
                    if (customer == null) {
                        System.out.println("Customer not found.");
                        break;
                    }

                    ShoppingCart cart = customer.getShoppingCart();
                    cart.clearCart(); // Clear previous items for a new order process

                    String productIdToAdd;
                    do {
                        System.out.print("Enter Product ID to add to order (or -1 to complete): ");
                        productIdToAdd = scanner.nextLine();
                        if (!productIdToAdd.equals("-1")) {
                            Product product = productService.getProductById(productIdToAdd);
                            if (product != null) {
                                System.out.print("Enter quantity: ");
                                int quantity = getIntInput();
                                if (quantity > 0) {
                                    cart.addItem(product, quantity);
                                } else {
                                    System.out.println("Quantity must be positive.");
                                }
                            } else {
                                System.out.println("Product not found.");
                            }
                        }
                    } while (!productIdToAdd.equals("-1"));

                    if (!cart.getItems().isEmpty()) {
                        orderService.placeOrder(customer, cart.getItems());
                        cart.clearCart(); // Clear cart after placing order
                    } else {
                        System.out.println("No items in cart. Order not placed.");
                    }
                    break;
                case 4:
                    System.out.print("Enter Customer ID to view orders: ");
                    String viewOrdersCustomerId = scanner.nextLine();
                    orderService.listOrdersForCustomer(viewOrdersCustomerId);
                    break;
                case 5:
                    productService.listAllProducts();
                    break;
                case 6:
                    System.out.println("Exiting Customer Menu...");
                    break;
                default:
                    System.out.println("Invalid option. Please try again.");
            }
        } while (choice != 6);
    }
}
