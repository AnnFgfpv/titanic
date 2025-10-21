# 🔒 Security Notice / Уведомление о безопасности

## ⚠️ Важное предупреждение / Important Warning

**English:**
This is a **DEMO/EDUCATIONAL PROJECT** for learning microservices architecture and API testing. 

**DO NOT use this code in production without proper security hardening!**

### Demo Credentials
The project includes a simple user system for educational purposes:
- **First registered user**: Automatically becomes **admin** (full access)
- **Other users**: Automatically become **user** (limited access)
- **JWT Secret**: Demo value in `.env` file (must be changed for production!)

This "first user = admin" approach is **INTENTIONALLY SIMPLE** to make the project easy to use for learning and testing.

**Русский:**
Это **ДЕМОНСТРАЦИОННЫЙ/УЧЕБНЫЙ ПРОЕКТ** для изучения микросервисной архитектуры и тестирования API.

**НЕ используйте этот код в production без надлежащего усиления безопасности!**

### Демо учетные данные
Проект использует простую систему пользователей для образовательных целей:
- **Первый зарегистрированный пользователь**: Автоматически становится **admin** (полный доступ)
- **Остальные пользователи**: Автоматически становятся **user** (ограниченный доступ)
- **JWT Secret**: Демо значение в файле `.env` (должно быть изменено для production!)

Подход "первый пользователь = admin" **НАМЕРЕННО ПРОСТОЙ**, чтобы сделать проект удобным для обучения и тестирования.

---

## 🛡️ For Production Use / Для использования в Production

If you want to use this project as a base for a real application, you **MUST**:

### 1. Change JWT Secret Key
```bash
# Generate a strong random secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Set it in .env file or environment
JWT_SECRET_KEY=<your-generated-secret>
```

### 2. Implement Proper User Management
The "first user = admin" approach is only for demos. In production:
- Implement proper admin invitation/assignment system
- Add email verification for registration
- Implement password reset functionality

### 3. Use a Real Database
Replace in-memory storage with PostgreSQL, MongoDB, or another production-grade database.

### 4. Add HTTPS/TLS
- Use reverse proxy (Nginx, Traefik)
- Add SSL certificates (Let's Encrypt)
- Force HTTPS for all connections

### 5. Add Rate Limiting
Implement rate limiting to prevent brute-force attacks and DDoS.

### 6. Security Headers
Add security headers:
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

### 7. Input Validation
Enhance input validation and sanitization beyond basic Pydantic validation.

### 8. Logging & Monitoring
- Add comprehensive logging
- Set up monitoring (Prometheus, Grafana)
- Configure alerts for suspicious activity

### 9. Secrets Management
Use proper secrets management:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets
- Docker Secrets

### 10. Regular Updates
Keep all dependencies up to date and monitor for security vulnerabilities.

---

## 📝 Environment Variables / Переменные окружения

### Required for Production:
- `JWT_SECRET_KEY` - **MUST be changed!** Generate a strong random value
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 15)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiration (default: 7)

### Optional:
- `AUTH_SERVICE_URL` - Auth service URL
- `PASSENGER_SERVICE_URL` - Passenger service URL
- `STATS_SERVICE_URL` - Statistics service URL

---

## 🔍 Security Checklist / Чеклист безопасности

Before deploying to production / Перед деплоем в production:

- [ ] Changed JWT_SECRET_KEY to a strong random value
- [ ] Removed or changed default user passwords
- [ ] Replaced in-memory storage with a real database
- [ ] Added HTTPS/TLS encryption
- [ ] Implemented rate limiting
- [ ] Added security headers
- [ ] Enhanced input validation
- [ ] Set up logging and monitoring
- [ ] Configured proper secrets management
- [ ] Updated all dependencies to latest secure versions
- [ ] Performed security audit/penetration testing
- [ ] Reviewed all exposed endpoints
- [ ] Configured proper CORS settings (not allow_origins=["*"])
- [ ] Added backup and disaster recovery procedures

---

## 📧 Responsible Disclosure / Ответственное раскрытие

If you find a security vulnerability in this educational project, please:
1. **DO NOT** create a public GitHub issue
2. Email the details to the repository owner
3. Allow reasonable time for a fix before public disclosure

---

## 📜 License & Disclaimer / Лицензия и отказ от ответственности

This project is provided **"AS IS"** without warranty of any kind. The authors are not responsible for any security issues arising from the use of this code.

Use at your own risk!

---

**Remember**: This is a **learning project**. Real production systems require much more comprehensive security measures! 🔐

