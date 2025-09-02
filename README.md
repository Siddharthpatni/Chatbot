# SmartBot 🤖

*A lightweight, offline-first chatbot built with Python and ReactJS*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

SmartBot is a lightweight chatbot solution that combines Python backend processing with a modern ReactJS frontend. Originally developed as a CLI tool, it has evolved into a web-based application that uses CSV-based Q&A logic, making it perfect for educational institutions, IT departments, and enterprise applications.

## ✨ Key Features

- **🔒 Offline-First**: No external APIs required - works completely offline
- **📊 CSV-Based Knowledge**: Easy-to-edit CSV files for questions and answers
- **⚡ Fast & Lightweight**: Minimal resource requirements
- **🌐 Web Interface**: Modern ReactJS frontend with responsive design
- **⏰ Time-Aware**: Built-in time consciousness for contextual responses
- **🔧 Modular Architecture**: Easy to extend and customize
- **💰 Zero Subscription Cost**: No ongoing fees or API charges
- **🚀 Easy Deployment**: Works on local machines and cloud platforms

## 🏗️ Architecture

### Technology Stack
- **Frontend**: ReactJS, JavaScript (JSX), CSS3
- **Backend**: Python, Flask
- **Data Storage**: CSV files
- **Dependencies**: Flask, csv, datetime, argparse

### File Structure
```
smartbot/
├── backend/
│   └── app.py              # Flask backend server
├── frontend/
│   ├── public/             # Static assets
│   └── src/
│       ├── App.js          # Main React component
│       └── App.css         # Styling
├── templates/              # HTML templates
└── questions.csv           # Q&A knowledge base
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smartbot.git
   cd smartbot
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install flask
   python app.py
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:3000`

## 📋 Use Cases

### 🎓 Education Sector
**Problem**: Students and staff repeatedly ask the same questions.
**Solution**: SmartBot serves as a 24/7 automated FAQ assistant.

### 🏢 Customer Support
**Problem**: High volume of repetitive queries (e.g., password resets).
**Solution**: CSV-based knowledge database for instant answers.

### 👨‍💻 Developer Tools
**Problem**: Frequent requests for code syntax/API references.
**Solution**: Quick-access coding assistant for common queries.

## 🔧 Configuration

### Adding New Questions
Edit the `questions.csv` file to add new Q&A pairs:
```csv
Question,Answer,Category
"How to reset password?","Contact IT support at ext. 1234","Support"
"What are office hours?","Monday-Friday, 9 AM - 5 PM","General"
```

### Customizing Responses
Modify the backend logic in `app.py` to customize how responses are processed and returned.

## 🆚 Comparison with Generic Chatbots

| Feature | SmartBot CLI | Generic Chatbots |
|---------|-------------|------------------|
| Offline Usage | ✅ Yes | ❌ No (Cloud-dependent) |
| CSV Customization | ✅ Yes | ❌ No (Hard-coded) |
| Time Awareness | ✅ Yes | ❌ No |
| Subscription Free | ✅ Yes | ❌ Paid plans |
| Easy Hosting | ✅ Local & Cloud | ❌ Provider-dependent |

## 🔮 Future Enhancements

- [ ] Natural Language Processing (NLP) integration
- [ ] Multi-language support
- [ ] RESTful API endpoints
- [ ] Advanced analytics and reporting
- [ ] Machine learning-based response improvement
- [ ] Integration with popular messaging platforms

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you have any questions or need help with setup, please open an issue or contact our team.

---

*"Ask SmartBot anything – get structured answers instantly!"* 🚀

## ⭐ Show Your Support

If this project helped you, please consider giving it a star on GitHub!
