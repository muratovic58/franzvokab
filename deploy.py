#!/usr/bin/env python
import os
import subprocess
import sys
import time

def run_command(command, description=None):
    """Run a command and print its output"""
    if description:
        print(f"\n{description}...")
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(line, end='')
    
    for line in process.stderr:
        print(line, end='', file=sys.stderr)
    
    process.wait()
    return process.returncode

def check_requirements():
    """Check if all required tools are installed"""
    print("Checking requirements...")
    
    # Check Git
    if run_command("git --version", "Checking Git") != 0:
        print("Git is not installed. Please install Git and try again.")
        return False
    
    # Check Vercel CLI
    if run_command("vercel --version", "Checking Vercel CLI") != 0:
        print("Vercel CLI is not installed. Installing...")
        if run_command("npm install -g vercel") != 0:
            print("Failed to install Vercel CLI. Please install it manually with 'npm install -g vercel'")
            return False
    
    # Check if logged in to Vercel
    if run_command("vercel whoami", "Checking Vercel login") != 0:
        print("You are not logged in to Vercel. Please login with 'vercel login'")
        return False
    
    return True

def deploy_to_vercel():
    """Deploy the application to Vercel"""
    print("\n=== Deploying to Vercel ===\n")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Creating .env file from .env.example...")
        with open(".env.example", "r") as example_file:
            example_content = example_file.read()
        
        with open(".env", "w") as env_file:
            env_file.write(example_content)
        
        print("Please edit the .env file with your Railway PostgreSQL connection string.")
        print("Press Enter when done...")
        input()
    
    # Deploy to Vercel
    if run_command("vercel --prod", "Deploying to Vercel") != 0:
        print("Failed to deploy to Vercel.")
        return False
    
    print("\nDeployment successful!")
    return True

def initialize_database():
    """Initialize the database on Railway"""
    print("\n=== Initializing Database ===\n")
    
    # Pull environment variables from Vercel
    if run_command("vercel env pull .env.production", "Pulling environment variables from Vercel") != 0:
        print("Failed to pull environment variables from Vercel.")
        return False
    
    # Set environment variables from .env.production
    with open(".env.production", "r") as env_file:
        for line in env_file:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
    
    # Run database setup
    print("Initializing database...")
    try:
        from setup_db import setup_database
        setup_database()
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return False

def main():
    """Main deployment script"""
    print("=== FranzVokab Deployment Script ===")
    
    if not check_requirements():
        return
    
    # Ensure all changes are committed
    if run_command("git status --porcelain") != "":
        print("\nYou have uncommitted changes. Please commit them before deploying.")
        choice = input("Would you like to commit all changes now? (y/n): ")
        if choice.lower() == 'y':
            commit_message = input("Enter commit message: ")
            run_command(f"git add .")
            run_command(f"git commit -m \"{commit_message}\"")
        else:
            return
    
    # Deploy to Vercel
    if not deploy_to_vercel():
        return
    
    # Initialize database
    choice = input("\nWould you like to initialize the database? (y/n): ")
    if choice.lower() == 'y':
        initialize_database()
    
    print("\n=== Deployment Complete ===")
    print("Your FranzVokab application is now live on Vercel with PostgreSQL on Railway!")

if __name__ == "__main__":
    main()
