# omg - Ongoing Mistake Grinder · [![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Reddan/omg/blob/master/LICENSE) [![pypi](https://img.shields.io/pypi/v/omg)](https://pypi.org/project/omg/) [![pypi](https://img.shields.io/pypi/pyversions/omg)](https://pypi.org/project/omg/)

A hot reload tool for Python.
Run your script with `omg`, and every time you save a file, it kills your code and brings it back. Only user modules are reloaded - external libraries are spared the pain - so it's fast. Disturbingly fast.

Great for prototyping, experimenting, or just punishing your code until it stops screaming. Jupyter promised flexibility and gave you state soup - `omg` gives you a clean kill and a fresh start every time.

---

## 📦 Install

```bash
pip install omg
```

---

## 🚀 Usage

Replace `python` with `omg`:

```bash
omg path/to/script.py
```

Make a change → `omg` reloads → repeat until the code obeys.

---

## 🤔 Why You'd Use It

* Faster than restarting Python every 12 seconds
* You don't trust Jupyter anymore
* You like your experiments linear and repeatable
* You want to hold onto in-memory results (`checkpointer` helps with that)

---

## 🧨 What It Actually Does

* Watches your `.py` files for changes
* Nukes and reloads all user modules
* Skips external libs - only *your* mess gets reloaded
* Re-runs your program from the top
* Doesn't care how cursed your codebase is

---

## Bonus: Keep Data Alive

Use [`checkpointer`](https://github.com/Reddan/checkpointer) if you want to keep results or cache expensive work across reloads.
It plays well with `omg` and saves you from recomputing your sins.

---

It grinds. You code. It reloads your mistakes with incredible speed.\
It doesn't fix them. 💀
