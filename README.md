# Client-Server Appointment Booking System

## Overview
The **Client-Server Appointment Booking System** is a network-based application designed to manage appointment reservations through a structured client-server architecture.

The system allows users to view available appointment slots through a client interface and request reservations. A central server processes all requests and ensures that appointments are scheduled without conflicts, preventing issues such as double bookings.

This project demonstrates how networking concepts can be applied to solve real-world scheduling problems through reliable communication between clients and a server.

---

## Problem Statement

Scheduling appointments is an essential task in many real-world environments, including:

- Healthcare services
- Business meetings
- University offices
- Customer service centers

Without a properly organized system, managing appointments can become complex and may lead to scheduling conflicts and confusion for both users and service providers.

This project addresses these issues by implementing a centralized system that manages and validates appointment reservations.

---

## System Architecture

The system follows a **client-server model**.

### Client
The client application allows users to:

- View available appointment slots
- Request reservation of an appointment
- Receive confirmation or denial of requests

### Server
The server is responsible for:

- Managing all appointment scheduling data
- Processing reservation requests
- Preventing conflicts such as double booking
- Ensuring that each appointment slot can only be reserved by one user

If a user attempts to reserve a slot that has already been taken, the server will deny the request.

---

## Key Features

- Client-server architecture
- Viewing available appointment slots
- Requesting appointment reservations
- Server-side conflict detection
- Prevention of double booking
- Real-time request processing

---

## Testing

This project uses pytest for automated testing of the server-client workflow.
The tests validate:

- State transitions
- Input validation and error handling
- Back navigation functionality
- Partial booking flow
- Multi-client concurrency handling

---


## Educational Purpose

This project demonstrates several important networking and software design concepts:

- Client-server communication
- Request/response protocols
- Network-based application design
- Data consistency and conflict prevention
- Practical application of networking concepts to real-world problems

---

## Future Improvements

This system can be expanded with additional features, such as:

- User authentication and login
- Appointment cancellation and rescheduling
- Graphical user interface (GUI)
- Database integration for persistent storage
- Notifications or reminders
- Multi-service scheduling support

---

## Team Members

- Angel Paul Antipolo  
- William Dawson  
- Estefania Ramirez  
- Zachary Smith  
- Tugba Agdas  
