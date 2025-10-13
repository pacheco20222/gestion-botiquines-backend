"""
Landing page routes for the VitalStock marketing site.
"""

from flask import Blueprint, render_template_string

bp = Blueprint("landing", __name__)

# Simple HTML template for the landing page
LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VitalStock - Smart First Aid Kit Management</title>
    <meta name="description" content="Revolutionary smart first aid kit management system with real-time monitoring and automated restocking.">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-links a {
            color: white;
            text-decoration: none;
            transition: opacity 0.3s;
        }
        
        .nav-links a:hover {
            opacity: 0.8;
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 120px 0 80px;
            text-align: center;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .hero p {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .cta-button {
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.1rem;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        }
        
        /* Features Section */
        .features {
            padding: 80px 0;
            background: #f8f9fa;
        }
        
        .features h2 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: #333;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .feature-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #667eea;
        }
        
        /* About Section */
        .about {
            padding: 80px 0;
            background: white;
        }
        
        .about-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
        }
        
        .about-text h2 {
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            color: #333;
        }
        
        .about-text p {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #666;
        }
        
        .about-image {
            text-align: center;
        }
        
        .about-image img {
            max-width: 100%;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        /* Footer */
        footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem 0;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero p {
                font-size: 1.1rem;
            }
            
            .about-content {
                grid-template-columns: 1fr;
            }
            
            .nav-links {
                display: none;
            }
        }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo">VitalStock</div>
            <ul class="nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <h1>Smart First Aid Kit Management</h1>
                <p>Revolutionary IoT-powered system for real-time monitoring, automated restocking, and intelligent inventory management of first aid supplies.</p>
                <a href="/login" class="cta-button">Get Started</a>
            </div>
        </section>

        <section class="features" id="features">
            <div class="container">
                <h2>Why Choose VitalStock?</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3>Real-Time Monitoring</h3>
                        <p>Track inventory levels, expiry dates, and usage patterns with our advanced IoT sensors and analytics dashboard.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🤖</div>
                        <h3>Automated Alerts</h3>
                        <p>Get instant notifications for low stock, expired medications, and maintenance requirements to ensure safety compliance.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📱</div>
                        <h3>Mobile Dashboard</h3>
                        <p>Access your first aid kit status anywhere with our responsive web application and mobile-optimized interface.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🏥</div>
                        <h3>Healthcare Compliance</h3>
                        <p>Meet regulatory requirements with automated reporting, audit trails, and compliance monitoring features.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💰</div>
                        <h3>Cost Optimization</h3>
                        <p>Reduce waste and optimize inventory with predictive analytics and smart reorder recommendations.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <h3>Secure & Reliable</h3>
                        <p>Enterprise-grade security with encrypted data transmission and 99.9% uptime guarantee.</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="about" id="about">
            <div class="container">
                <div class="about-content">
                    <div class="about-text">
                        <h2>Revolutionizing Healthcare Inventory</h2>
                        <p>VitalStock is a cutting-edge IoT solution designed to transform how healthcare facilities, schools, offices, and emergency services manage their first aid supplies.</p>
                        <p>Our smart sensors provide real-time weight monitoring, while our AI-powered platform delivers intelligent insights for optimal inventory management.</p>
                        <p>Join the future of healthcare inventory management with VitalStock.</p>
                    </div>
                    <div class="about-image">
                        <img src="/static/med-1.jpg" alt="Smart First Aid Kit Management" />
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer id="contact">
        <div class="container">
            <p>&copy; 2024 VitalStock. All rights reserved. | Smart First Aid Kit Management System</p>
        </div>
    </footer>
</body>
</html>
"""

@bp.route("/")
def landing():
    """Serve the landing page"""
    return render_template_string(LANDING_TEMPLATE)

@bp.route("/landing")
def landing_alt():
    """Alternative route for landing page"""
    return render_template_string(LANDING_TEMPLATE)
