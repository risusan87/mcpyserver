# 🧱 Project Pyncraft
![Top Lang](https://img.shields.io/github/languages/top/risusan87/mcpyserver)
![Repo Size](https://img.shields.io/github/repo-size/risusan87/mcpyserver)
![Commit Activity](https://img.shields.io/github/commit-activity/m/risusan87/mcpyserver)
![Last Commit](https://img.shields.io/github/last-commit/risusan87/mcpyserver)
![Issues](https://img.shields.io/github/issues/risusan87/mcpyserver)
![PRs](https://img.shields.io/github/issues-pr/risusan87/mcpyserver)



Pyncraft is a work-in-progress reimplementation of the official Minecraft Java Edition server ("Notchian server") written in Python.  
It aims to mimic the original server's behavior while providing a more accessible and modifiable codebase for further modification such as plugins, or even lower level base modification.

Python version tested is 3.12.<br>
To test its behavior, just clone the repo, install dependencies, then run:
```
$ python -m core
```

## 🚀 Project Goals 🚀

Pyncraft is not only a full replacement for vanilla server. Its main goals are:
- 👩🏻‍💻 **Learnability**: ✅ Make net.minecraft.server mechanics easier to explore and understand
- 🛠️ **Hackability**: ✅ Lower barrier for modding in Python, possibly, other Java-based pre-built plugins adaption such as Spigot plugins.
- ⚡ **Experimentation**: ✅ Prototype world gen, mob AI, or any sort of world behavior (possibly with GPU accerelation)

## 🤝 Contribution 🤝

Python version tested 3.12 may change for any other reasonable purpose for stable development.

This section is not meant to be a summer course teaching you how Notchian logic internally works, so start by understanding logic by visiting some wikipedia projects.<br>
At bare minimum, you must understand difference between logical server side and client side of logic. It is worth noting that you know what is possible and what's not on each sides. Furthermore, There is a difference between "logical" server and "dedicated" server. In short, dedicated server is physical, more abstract server existence in terms of logic that network modules can use to serialize into packets, and logical server is what defines the whole minecraft logic.
- About sides in Minecraft, refer:<br>
https://docs.minecraftforge.net/en/latest/concepts/sides/

- For notchian minecraft logic, refer to wikipedia projects:<br>
https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge

- For notchian network protocol, refer:<br>
https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Protocol

Official Minecraft is in continuous heavy progression for adding new features and introducing new major versions almost every a few year.<br>
If wiki projects ever become outdated, consider reverse-engineer the code directly.<br>
https://minecraft.fandom.com/wiki/Tutorials/See_Minecraft%27s_code

The link above is partially outdated, modern MC versions 1.17+ use Tiny v2 mapping format.<br>
For example, if you want to use SpecialSource to deobfuscate the code, you must first convert Tiny into srg format:
```
Tiny v2:
com.mojang.math.Constants -> b:
# {"fileName":"Constants.java","id":"sourceFile"}
    float PI -> a
    float RAD_TO_DEG -> b
    float DEG_TO_RAD -> c
    float EPSILON -> d
    3:3:void <init>() -> <init>
```
```
srg:
CL: b com/mojang/math/Constants
FD: b/a com/mojang/math/Constants/PI
FD: b/b com/mojang/math/Constants/RAD_TO_DEG
FD: b/c com/mojang/math/Constants/DEG_TO_RAD
FD: b/d com/mojang/math/Constants/EPSILON
MD: b/<init> ()V com/mojang/math/Constants/<init> ()V
```




