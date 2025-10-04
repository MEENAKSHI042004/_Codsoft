#!/usr/bin/env python3
"""
Contact Book CLI
Features:
- Add Contact (name, phone, email, address)
- View Contact List
- Search Contact (by name or phone, partial match)
- Update Contact
- Delete Contact
- Persistent storage to contacts.json
"""

import json
import os
import re
from typing import List, Dict

DATA_FILE = "contacts.json"

def load_contacts() -> List[Dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_contacts(contacts: List[Dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

def valid_phone(phone: str) -> bool:
    # Allow digits, spaces, +, -, parentheses; require at least 6 digits
    digits = re.sub(r"\D", "", phone)
    return len(digits) >= 6

def valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def prompt_contact(existing: Dict = None) -> Dict:
    existing = existing or {}
    name = input(f"Name [{existing.get('name','')}]: ").strip() or existing.get("name","")
    while not name:
        print("Name cannot be empty.")
        name = input("Name: ").strip()

    phone = input(f"Phone [{existing.get('phone','')}]: ").strip() or existing.get("phone","")
    while phone and not valid_phone(phone):
        print("Invalid phone. Use at least 6 digits; allowed characters: digits, + - () space.")
        phone = input("Phone: ").strip()

    email = input(f"Email [{existing.get('email','')}]: ").strip() or existing.get("email","")
    while email and not valid_email(email):
        print("Invalid email format.")
        email = input("Email: ").strip()

    address = input(f"Address [{existing.get('address','')}]: ").strip() or existing.get("address","")

    return {"name": name, "phone": phone, "email": email, "address": address}

def add_contact(contacts: List[Dict]):
    print("\n--- Add Contact ---")
    contact = prompt_contact()
    contacts.append(contact)
    save_contacts(contacts)
    print(f"Contact '{contact['name']}' added.\n")

def view_contacts(contacts: List[Dict]):
    print("\n--- Contact List ---")
    if not contacts:
        print("No contacts saved.\n")
        return
    for i, c in enumerate(contacts, 1):
        print(f"{i}. {c.get('name','')}")
        print(f"   Phone:   {c.get('phone','')}")
        print(f"   Email:   {c.get('email','')}")
        print(f"   Address: {c.get('address','')}\n")

def search_contacts(contacts: List[Dict], term: str) -> List[int]:
    term = term.lower().strip()
    results = []
    for idx, c in enumerate(contacts):
        if term in c.get("name","").lower() or term in c.get("phone","").lower():
            results.append(idx)
    return results

def show_search_results(contacts: List[Dict], indices: List[int]):
    if not indices:
        print("No matches found.")
        return
    for rank, idx in enumerate(indices, 1):
        c = contacts[idx]
        print(f"{rank}. [{idx+1}] {c.get('name','')} - {c.get('phone','')} - {c.get('email','')}")

def update_contact(contacts: List[Dict]):
    print("\n--- Update Contact ---")
    term = input("Search by name or phone: ").strip()
    if not term:
        print("Search term required.\n"); return
    hits = search_contacts(contacts, term)
    if not hits:
        print("No contacts matched.\n"); return
    show_search_results(contacts, hits)
    choice = input("Enter the number of the result to update (or index shown in [ ]): ").strip()
    if not choice:
        print("No selection made.\n"); return

    # allow either the result rank (1..n) or the absolute index shown in [ ]
    selected_idx = None
    if choice.isdigit():
        num = int(choice)
        # try rank first
        if 1 <= num <= len(hits):
            selected_idx = hits[num-1]
        else:
            # maybe user typed absolute index
            if 1 <= num <= len(contacts):
                selected_idx = num-1

    if selected_idx is None:
        print("Invalid selection.\n"); return

    print("\nEnter new values (leave blank to keep current):")
    updated = prompt_contact(existing=contacts[selected_idx])
    contacts[selected_idx] = updated
    save_contacts(contacts)
    print(f"Contact updated: {updated['name']}\n")

def delete_contact(contacts: List[Dict]):
    print("\n--- Delete Contact ---")
    term = input("Search by name or phone: ").strip()
    if not term:
        print("Search term required.\n"); return
    hits = search_contacts(contacts, term)
    if not hits:
        print("No contacts matched.\n"); return
    show_search_results(contacts, hits)
    choice = input("Enter number of result to delete (or index shown in [ ]) (leave blank to cancel): ").strip()
    if not choice:
        print("Canceled.\n"); return

    selected_idx = None
    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(hits):
            selected_idx = hits[num-1]
        else:
            if 1 <= num <= len(contacts):
                selected_idx = num-1

    if selected_idx is None:
        print("Invalid selection.\n"); return

    confirm = input(f"Are you sure you want to delete '{contacts[selected_idx]['name']}'? (y/n): ").strip().lower()
    if confirm == "y":
        removed = contacts.pop(selected_idx)
        save_contacts(contacts)
        print(f"Deleted contact: {removed['name']}\n")
    else:
        print("Deletion canceled.\n")

def main_menu():
    contacts = load_contacts()
    actions = {
        "1": ("Add Contact", add_contact),
        "2": ("View Contact List", view_contacts),
        "3": ("Search Contact", lambda c: _search_flow(c)),
        "4": ("Update Contact", update_contact),
        "5": ("Delete Contact", delete_contact),
        "6": ("Exit", None),
    }

    while True:
        print("===== Contact Book =====")
        for k, (label, _) in actions.items():
            print(f"{k}. {label}")
        choice = input("Choose an option: ").strip()
        if choice == "6":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if not action:
            print("Invalid choice. Try again.\n")
            continue
        # call the function with contacts
        func = action[1]
        func(contacts)

def _search_flow(contacts):
    term = input("Enter name or phone to search: ").strip()
    if not term:
        print("Search term required.\n"); return
    hits = search_contacts(contacts, term)
    if not hits:
        print("No matches found.\n"); return
    show_search_results(contacts, hits)
    print("")  # spacing

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")
