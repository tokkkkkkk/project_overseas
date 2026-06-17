from flask import Flask, flash, redirect, render_template, request, url_for

# 2. Database & ORM
from models import Utenti
from sqlalchemy import func

# 3. Security & Hashing (Flask-Bcrypt replaces passlib)
from flask_bcrypt import Bcrypt
