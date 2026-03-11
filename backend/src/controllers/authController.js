import { db } from "../config/db.js";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";

export const register = async (req, res) => {
  const { name, email, password } = req.body;

  if (!name || !email || !password) {
    return res.status(400).json({ message: "Preencha todos os campos" });
  }

  const [userExists] = await db.query(
    "SELECT id FROM users WHERE email = ?",
    [email]
  );

  if (userExists.length > 0) {
    return res.status(400).json({ message: "Email já cadastrado" });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  await db.query(
    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
    [name, email, hashedPassword]
  );

  res.status(201).json({ message: "Usuário criado com sucesso" });
};

export const login = async (req, res) => {
  const { email, password } = req.body;

  const [users] = await db.query(
    "SELECT * FROM users WHERE email = ?",
    [email]
  );

  if (users.length === 0) {
    return res.status(401).json({ message: "Email ou senha inválidos" });
  }

  const user = users[0];
  const isValid = await bcrypt.compare(password, user.password);

  if (!isValid) {
    return res.status(401).json({ message: "Email ou senha inválidos" });
  }

  const token = jwt.sign(
    { id: user.id },
    process.env.JWT_SECRET,
    { expiresIn: "1d" }
  );

  res.json({ token, name: user.name });
};
