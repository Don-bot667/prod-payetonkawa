# Guide Complet - Site E-commerce PayeTonKawa

Ce guide explique comment creer le site e-commerce PayeTonKawa avec Astro et Tailwind CSS.

---

## RESUME DU PROJET

**PayeTonKawa** est un site e-commerce de vente de cafe. Les clients peuvent :
- Voir le catalogue des produits
- S'inscrire et se connecter
- Ajouter des produits au panier
- Passer des commandes
- Voir l'historique de leurs commandes

### Technologies utilisees
- **Astro** : Framework web moderne
- **Tailwind CSS** : Styles CSS utilitaires
- **TypeScript** : JavaScript avec types
- **LocalStorage** : Stockage du panier et session

### APIs utilisees
| API | Port | Utilisation |
|-----|------|-------------|
| Clients | 8000 | Inscription, connexion, profil |
| Produits | 8001 | Catalogue, details produits |
| Commandes | 8002 | Passer commande, historique |

---

## STRUCTURE DU PROJET

```
sitepayetonkawa/
├── astro.config.mjs          <- Configuration Astro
├── tailwind.config.mjs       <- Configuration Tailwind
├── tsconfig.json             <- Configuration TypeScript
├── package.json              <- Dependances
├── public/
│   └── favicon.svg           <- Icone du site
├── src/
│   ├── layouts/
│   │   └── Layout.astro      <- Structure commune (header, footer)
│   ├── components/
│   │   ├── Header.astro      <- Barre de navigation
│   │   ├── Footer.astro      <- Pied de page
│   │   ├── ProductCard.astro <- Carte produit (catalogue)
│   │   ├── CartIcon.astro    <- Icone panier avec compteur
│   │   └── Hero.astro        <- Banniere d'accueil
│   ├── lib/
│   │   ├── api.ts            <- Fonctions pour appeler les APIs
│   │   ├── auth.ts           <- Gestion de l'authentification
│   │   └── cart.ts           <- Gestion du panier (localStorage)
│   ├── pages/
│   │   ├── index.astro       <- Page d'accueil
│   │   ├── produits.astro    <- Catalogue des produits
│   │   ├── produit/
│   │   │   └── [id].astro    <- Detail d'un produit
│   │   ├── panier.astro      <- Page du panier
│   │   ├── connexion.astro   <- Page de connexion
│   │   ├── inscription.astro <- Page d'inscription
│   │   └── compte.astro      <- Espace client (commandes)
│   └── styles/
│       └── global.css        <- Styles globaux
└── guideSite.md              <- Ce fichier
```

---

## ETAPE 1 : CREER LE PROJET ASTRO

```bash
cd /Users/faouzdon/Desktop/payetonkawa/sitepayetonkawa
npm create astro@latest .
```

Reponses aux questions :
- **How would you like to start?** → `Empty`
- **Install dependencies?** → `Yes`
- **TypeScript?** → `Yes`
- **How strict?** → `Strict`
- **Initialize git?** → `No`

---

## ETAPE 2 : INSTALLER TAILWIND CSS

```bash
npx astro add tailwind
```

Reponds `Yes` a tout.

---

## ETAPE 3 : CREER LES DOSSIERS

```bash
mkdir -p src/layouts src/components src/lib src/styles src/pages/produit
```

---

## COMPRENDRE L'AUTHENTIFICATION (EXPLICATION SIMPLE)

### C'est quoi l'authentification ?

L'authentification permet de savoir **qui est l'utilisateur**. Sans elle, le site ne sait pas si c'est toi ou quelqu'un d'autre.

### Comment ca marche ? (Version simplifiee)

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSCRIPTION                                   │
│                                                                 │
│  1. L'utilisateur remplit le formulaire (nom, email, etc.)     │
│  2. On envoie les donnees a l'API Clients (POST /customers/)   │
│  3. L'API cree le client et retourne son ID                    │
│  4. On stocke l'ID dans le navigateur (localStorage)           │
│  5. L'utilisateur est maintenant "connecte"                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CONNEXION                                     │
│                                                                 │
│  1. L'utilisateur entre son email                              │
│  2. On demande a l'API la liste des clients (GET /customers/)  │
│  3. On cherche le client avec cet email                        │
│  4. Si trouve : on stocke son ID dans localStorage             │
│  5. Si pas trouve : message d'erreur                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    VERIFICATION                                  │
│                                                                 │
│  A chaque page, on verifie si localStorage contient un ID      │
│  - Si OUI : l'utilisateur est connecte, on affiche son nom     │
│  - Si NON : l'utilisateur n'est pas connecte                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    DECONNEXION                                   │
│                                                                 │
│  On supprime l'ID du localStorage                              │
│  L'utilisateur n'est plus connecte                             │
└─────────────────────────────────────────────────────────────────┘
```

### Ou est stockee la session ?

```javascript
// localStorage est un stockage dans le navigateur
// Les donnees restent meme si on ferme le navigateur

// Sauvegarder l'utilisateur connecte
localStorage.setItem('user', JSON.stringify({ id: 1, nom: 'Dupont', email: 'a@b.com' }));

// Recuperer l'utilisateur
const user = JSON.parse(localStorage.getItem('user'));

// Supprimer (deconnexion)
localStorage.removeItem('user');
```

### Schema du flux d'authentification

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  ACCUEIL │────>│ CONNEXION│────>│  API     │────>│ COMPTE   │
│          │     │          │     │ CLIENTS  │     │          │
│ [Se      │     │ Email:   │     │          │     │ Bonjour  │
│ connecter│     │ [____]   │     │ Verifie  │     │ Jean !   │
│ ]        │     │          │     │ l'email  │     │          │
└──────────┘     │ [Valider]│     │          │     │ Mes      │
                 └──────────┘     │ Retourne │     │ commandes│
                                  │ le client│     └──────────┘
                                  └──────────┘
```

### Securite (Important a comprendre)

**Cette methode est SIMPLIFIEE pour un projet scolaire.**

Dans un vrai site e-commerce, on utiliserait :
- Un **mot de passe** (hashe, jamais en clair)
- Un **token JWT** (jeton securise)
- Une **API d'authentification** dediee
- Du **HTTPS** obligatoire

Pour ce projet MSPR, on utilise une version simplifiee car :
1. L'API Clients n'a pas de champ mot de passe
2. C'est plus simple a comprendre
3. C'est suffisant pour une demonstration

---

## COMPRENDRE LE PANIER (EXPLICATION SIMPLE)

### C'est quoi le panier ?

Le panier stocke les produits que l'utilisateur veut acheter, **avant** de passer commande.

### Ou est stocke le panier ?

Dans le **localStorage** du navigateur. Comme ca :
- Le panier reste meme si on actualise la page
- Le panier reste meme si on ferme le navigateur
- Chaque navigateur a son propre panier

### Structure du panier

```javascript
// Le panier est un tableau d'objets
const panier = [
    { produit_id: 1, nom: "Cafe Bresil", prix: 12.50, quantite: 2 },
    { produit_id: 3, nom: "Cafe Colombie", prix: 15.00, quantite: 1 }
];

// Stocke dans localStorage
localStorage.setItem('cart', JSON.stringify(panier));
```

### Operations sur le panier

```
┌─────────────────────────────────────────────────────────────────┐
│  AJOUTER AU PANIER                                              │
│                                                                 │
│  1. On recupere le panier actuel depuis localStorage           │
│  2. On cherche si le produit est deja dans le panier           │
│     - Si OUI : on augmente la quantite                         │
│     - Si NON : on ajoute le produit                            │
│  3. On sauvegarde le nouveau panier dans localStorage          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MODIFIER LA QUANTITE                                           │
│                                                                 │
│  1. On recupere le panier                                      │
│  2. On trouve le produit par son ID                            │
│  3. On modifie sa quantite                                     │
│  4. Si quantite = 0, on supprime le produit                    │
│  5. On sauvegarde                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PASSER COMMANDE                                                │
│                                                                 │
│  1. On verifie que l'utilisateur est connecte                  │
│  2. On transforme le panier en format API :                    │
│     { client_id: 5, lignes: [...] }                            │
│  3. On envoie a l'API Commandes (POST /orders/)                │
│  4. On vide le panier                                          │
│  5. On redirige vers "Mes commandes"                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## FICHIERS DU PROJET

---

### 1. `src/styles/global.css`

```css
/* Styles globaux */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Police */
body {
    font-family: 'Inter', system-ui, sans-serif;
}

/* Animations */
.fade-in {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Bouton hover effet */
.btn-primary {
    @apply bg-amber-600 text-white px-6 py-3 rounded-lg font-medium
           hover:bg-amber-700 transition-colors duration-200;
}

.btn-secondary {
    @apply border-2 border-amber-600 text-amber-600 px-6 py-3 rounded-lg font-medium
           hover:bg-amber-600 hover:text-white transition-colors duration-200;
}

/* Card hover */
.product-card {
    @apply transition-transform duration-200 hover:scale-105;
}
```

---

### 2. `src/lib/api.ts`

```typescript
// Configuration des APIs
const API_CLIENTS = "http://localhost:8000";
const API_PRODUITS = "http://localhost:8001";
const API_COMMANDES = "http://localhost:8002";

// ============ TYPES ============

export interface Client {
    id: number;
    nom: string;
    prenom: string;
    email: string;
    telephone?: string;
    adresse?: string;
}

export interface ClientCreate {
    nom: string;
    prenom: string;
    email: string;
    telephone?: string;
    adresse?: string;
}

export interface Produit {
    id: number;
    nom: string;
    description?: string;
    prix: number;
    stock: number;
    poids_kg: number;
    origine?: string;
}

export interface LigneCommande {
    id: number;
    produit_id: number;
    quantite: number;
    prix_unitaire: number;
}

export interface LigneCommandeCreate {
    produit_id: number;
    quantite: number;
    prix_unitaire: number;
}

export interface Commande {
    id: number;
    client_id: number;
    date_commande: string;
    statut: string;
    total: number;
    lignes: LigneCommande[];
}

export interface CommandeCreate {
    client_id: number;
    lignes: LigneCommandeCreate[];
}

// ============ CLIENTS ============

export async function getClients(): Promise<Client[]> {
    const response = await fetch(`${API_CLIENTS}/customers/`);
    if (!response.ok) throw new Error("Erreur API Clients");
    return response.json();
}

export async function getClient(id: number): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/${id}`);
    if (!response.ok) throw new Error("Client non trouve");
    return response.json();
}

export async function createClient(data: ClientCreate): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error("Erreur creation client");
    return response.json();
}

// ============ PRODUITS ============

export async function getProduits(): Promise<Produit[]> {
    const response = await fetch(`${API_PRODUITS}/products/`);
    if (!response.ok) throw new Error("Erreur API Produits");
    return response.json();
}

export async function getProduit(id: number): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/${id}`);
    if (!response.ok) throw new Error("Produit non trouve");
    return response.json();
}

// ============ COMMANDES ============

export async function getCommandes(): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/`);
    if (!response.ok) throw new Error("Erreur API Commandes");
    return response.json();
}

export async function getCommandesByClient(clientId: number): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/client/${clientId}`);
    if (!response.ok) throw new Error("Erreur recuperation commandes");
    return response.json();
}

export async function createCommande(data: CommandeCreate): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error("Erreur creation commande");
    return response.json();
}
```

---

### 3. `src/lib/auth.ts`

```typescript
/**
 * AUTHENTIFICATION SIMPLIFIEE
 *
 * Ce fichier gere la connexion/deconnexion des utilisateurs.
 * Les donnees sont stockees dans localStorage.
 *
 * IMPORTANT : C'est une version simplifiee pour un projet scolaire.
 * En production, on utiliserait des tokens JWT et des mots de passe hashes.
 */

import { getClients, createClient, type Client, type ClientCreate } from './api';

// Cle utilisee dans localStorage
const STORAGE_KEY = 'payetonkawa_user';

/**
 * Recupere l'utilisateur connecte
 * @returns L'utilisateur ou null si pas connecte
 */
export function getUser(): Client | null {
    if (typeof window === 'undefined') return null; // SSR check

    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    try {
        return JSON.parse(stored);
    } catch {
        return null;
    }
}

/**
 * Verifie si l'utilisateur est connecte
 */
export function isLoggedIn(): boolean {
    return getUser() !== null;
}

/**
 * Connecte un utilisateur par son email
 *
 * FONCTIONNEMENT :
 * 1. On recupere tous les clients depuis l'API
 * 2. On cherche celui qui a le meme email
 * 3. Si trouve, on le stocke dans localStorage
 *
 * @param email L'email de l'utilisateur
 * @returns Le client si trouve, sinon une erreur
 */
export async function login(email: string): Promise<Client> {
    // Recuperer tous les clients
    const clients = await getClients();

    // Chercher par email (insensible a la casse)
    const client = clients.find(c => c.email.toLowerCase() === email.toLowerCase());

    if (!client) {
        throw new Error("Aucun compte trouve avec cet email");
    }

    // Sauvegarder dans localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(client));

    return client;
}

/**
 * Inscrit un nouvel utilisateur
 *
 * FONCTIONNEMENT :
 * 1. On verifie que l'email n'existe pas deja
 * 2. On cree le client via l'API
 * 3. On le connecte automatiquement
 *
 * @param data Les informations du nouveau client
 * @returns Le client cree
 */
export async function register(data: ClientCreate): Promise<Client> {
    // Verifier si l'email existe deja
    const clients = await getClients();
    const exists = clients.some(c => c.email.toLowerCase() === data.email.toLowerCase());

    if (exists) {
        throw new Error("Un compte existe deja avec cet email");
    }

    // Creer le client
    const newClient = await createClient(data);

    // Le connecter automatiquement
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newClient));

    return newClient;
}

/**
 * Deconnecte l'utilisateur
 *
 * Supprime les donnees de localStorage
 */
export function logout(): void {
    localStorage.removeItem(STORAGE_KEY);
}
```

---

### 4. `src/lib/cart.ts`

```typescript
/**
 * GESTION DU PANIER
 *
 * Le panier est stocke dans localStorage.
 * Il persiste meme si on ferme le navigateur.
 */

// Cle utilisee dans localStorage
const CART_KEY = 'payetonkawa_cart';

// Structure d'un article dans le panier
export interface CartItem {
    produit_id: number;
    nom: string;
    prix: number;
    quantite: number;
    image?: string;
}

/**
 * Recupere le panier actuel
 */
export function getCart(): CartItem[] {
    if (typeof window === 'undefined') return []; // SSR check

    const stored = localStorage.getItem(CART_KEY);
    if (!stored) return [];

    try {
        return JSON.parse(stored);
    } catch {
        return [];
    }
}

/**
 * Sauvegarde le panier
 */
function saveCart(cart: CartItem[]): void {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));

    // Emettre un evenement pour mettre a jour l'interface
    window.dispatchEvent(new CustomEvent('cart-updated', { detail: cart }));
}

/**
 * Ajoute un produit au panier
 * Si le produit existe deja, augmente la quantite
 */
export function addToCart(item: Omit<CartItem, 'quantite'>, quantite: number = 1): void {
    const cart = getCart();

    // Chercher si le produit est deja dans le panier
    const existingIndex = cart.findIndex(i => i.produit_id === item.produit_id);

    if (existingIndex !== -1) {
        // Le produit existe, on augmente la quantite
        cart[existingIndex].quantite += quantite;
    } else {
        // Nouveau produit
        cart.push({ ...item, quantite });
    }

    saveCart(cart);
}

/**
 * Modifie la quantite d'un produit
 * Si quantite = 0, supprime le produit
 */
export function updateQuantity(produit_id: number, quantite: number): void {
    let cart = getCart();

    if (quantite <= 0) {
        // Supprimer le produit
        cart = cart.filter(i => i.produit_id !== produit_id);
    } else {
        // Mettre a jour la quantite
        const item = cart.find(i => i.produit_id === produit_id);
        if (item) {
            item.quantite = quantite;
        }
    }

    saveCart(cart);
}

/**
 * Supprime un produit du panier
 */
export function removeFromCart(produit_id: number): void {
    const cart = getCart().filter(i => i.produit_id !== produit_id);
    saveCart(cart);
}

/**
 * Vide le panier
 */
export function clearCart(): void {
    saveCart([]);
}

/**
 * Calcule le nombre total d'articles
 */
export function getCartCount(): number {
    return getCart().reduce((sum, item) => sum + item.quantite, 0);
}

/**
 * Calcule le total du panier
 */
export function getCartTotal(): number {
    return getCart().reduce((sum, item) => sum + (item.prix * item.quantite), 0);
}
```

---

### 5. `src/components/Header.astro`

```astro
---
// Header avec navigation
---

<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <!-- Logo -->
            <a href="/" class="flex items-center gap-2">
                <span class="text-2xl">☕</span>
                <span class="font-bold text-xl text-gray-900">PayeTonKawa</span>
            </a>

            <!-- Navigation -->
            <nav class="hidden md:flex items-center gap-8">
                <a href="/" class="text-gray-600 hover:text-amber-600 transition">Accueil</a>
                <a href="/produits" class="text-gray-600 hover:text-amber-600 transition">Nos Cafes</a>
            </nav>

            <!-- Actions -->
            <div class="flex items-center gap-4">
                <!-- Panier -->
                <a href="/panier" class="relative p-2 text-gray-600 hover:text-amber-600 transition">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                    <span id="cart-count" class="absolute -top-1 -right-1 bg-amber-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center hidden">0</span>
                </a>

                <!-- Compte -->
                <div id="user-menu">
                    <a href="/connexion" id="btn-login" class="text-gray-600 hover:text-amber-600 transition">
                        Connexion
                    </a>
                    <div id="user-logged" class="hidden flex items-center gap-4">
                        <a href="/compte" class="text-gray-600 hover:text-amber-600 transition">
                            <span id="user-name">Mon compte</span>
                        </a>
                        <button id="btn-logout" class="text-sm text-gray-500 hover:text-red-600 transition">
                            Deconnexion
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</header>

<script>
    import { getUser, logout } from '../lib/auth';
    import { getCartCount } from '../lib/cart';

    function updateUI() {
        const user = getUser();
        const btnLogin = document.getElementById('btn-login');
        const userLogged = document.getElementById('user-logged');
        const userName = document.getElementById('user-name');
        const cartCount = document.getElementById('cart-count');

        // Mettre a jour le compteur panier
        const count = getCartCount();
        if (cartCount) {
            if (count > 0) {
                cartCount.textContent = String(count);
                cartCount.classList.remove('hidden');
            } else {
                cartCount.classList.add('hidden');
            }
        }

        // Mettre a jour l'affichage connexion
        if (user) {
            btnLogin?.classList.add('hidden');
            userLogged?.classList.remove('hidden');
            if (userName) userName.textContent = user.prenom;
        } else {
            btnLogin?.classList.remove('hidden');
            userLogged?.classList.add('hidden');
        }
    }

    // Deconnexion
    document.getElementById('btn-logout')?.addEventListener('click', () => {
        logout();
        window.location.href = '/';
    });

    // Ecouter les changements du panier
    window.addEventListener('cart-updated', updateUI);

    // Init
    updateUI();
</script>
```

---

### 6. `src/components/Footer.astro`

```astro
---
// Footer du site
---

<footer class="bg-gray-900 text-white mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Logo et description -->
            <div>
                <div class="flex items-center gap-2 mb-4">
                    <span class="text-2xl">☕</span>
                    <span class="font-bold text-xl">PayeTonKawa</span>
                </div>
                <p class="text-gray-400 text-sm">
                    Les meilleurs cafes du monde, torrefies avec passion et livres chez vous.
                </p>
            </div>

            <!-- Liens -->
            <div>
                <h3 class="font-semibold mb-4">Navigation</h3>
                <ul class="space-y-2 text-gray-400 text-sm">
                    <li><a href="/" class="hover:text-white transition">Accueil</a></li>
                    <li><a href="/produits" class="hover:text-white transition">Nos Cafes</a></li>
                    <li><a href="/compte" class="hover:text-white transition">Mon compte</a></li>
                </ul>
            </div>

            <!-- Contact -->
            <div>
                <h3 class="font-semibold mb-4">Contact</h3>
                <ul class="space-y-2 text-gray-400 text-sm">
                    <li>contact@payetonkawa.fr</li>
                    <li>01 23 45 67 89</li>
                    <li>Paris, France</li>
                </ul>
            </div>
        </div>

        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
            <p>&copy; 2024 PayeTonKawa - Projet MSPR</p>
        </div>
    </div>
</footer>
```

---

### 7. `src/components/ProductCard.astro`

```astro
---
interface Props {
    id: number;
    nom: string;
    prix: number;
    origine?: string;
    image: string;
}

const { id, nom, prix, origine, image } = Astro.props;
---

<div class="product-card bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100">
    <a href={`/produit/${id}`}>
        <div class="aspect-square overflow-hidden">
            <img
                src={image}
                alt={nom}
                class="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
            />
        </div>
    </a>
    <div class="p-4">
        <a href={`/produit/${id}`}>
            <h3 class="font-semibold text-gray-900 hover:text-amber-600 transition">{nom}</h3>
        </a>
        {origine && <p class="text-sm text-gray-500 mt-1">Origine : {origine}</p>}
        <div class="flex items-center justify-between mt-3">
            <span class="text-lg font-bold text-amber-600">{prix.toFixed(2)} €</span>
            <button
                data-add-cart
                data-id={id}
                data-nom={nom}
                data-prix={prix}
                class="bg-amber-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-amber-700 transition"
            >
                Ajouter
            </button>
        </div>
    </div>
</div>

<script>
    import { addToCart } from '../lib/cart';

    document.querySelectorAll('[data-add-cart]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget as HTMLElement;
            const id = parseInt(target.dataset.id!);
            const nom = target.dataset.nom!;
            const prix = parseFloat(target.dataset.prix!);

            addToCart({ produit_id: id, nom, prix });

            // Feedback visuel
            target.textContent = 'Ajoute !';
            target.classList.add('bg-green-600');
            setTimeout(() => {
                target.textContent = 'Ajouter';
                target.classList.remove('bg-green-600');
            }, 1000);
        });
    });
</script>
```

---

### 8. `src/components/Hero.astro`

```astro
---
// Banniere d'accueil
---

<section class="relative bg-gradient-to-r from-amber-900 to-amber-700 text-white">
    <div class="absolute inset-0 bg-black/30"></div>
    <div
        class="absolute inset-0 bg-cover bg-center opacity-30"
        style="background-image: url('https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1920&q=80')"
    ></div>

    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
        <div class="max-w-2xl">
            <h1 class="text-4xl md:text-5xl font-bold mb-6">
                Le cafe d'exception,<br/>livre chez vous
            </h1>
            <p class="text-xl text-amber-100 mb-8">
                Decouvrez notre selection de cafes premium, torrefies artisanalement
                et provenant des meilleures plantations du monde.
            </p>
            <div class="flex flex-wrap gap-4">
                <a href="/produits" class="btn-primary">
                    Decouvrir nos cafes
                </a>
                <a href="/inscription" class="btn-secondary border-white text-white hover:bg-white hover:text-amber-900">
                    Creer un compte
                </a>
            </div>
        </div>
    </div>
</section>
```

---

### 9. `src/layouts/Layout.astro`

```astro
---
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import '../styles/global.css';

interface Props {
    title: string;
}

const { title } = Astro.props;
---

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="PayeTonKawa - Cafe d'exception livre chez vous">
    <title>{title} | PayeTonKawa</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="min-h-screen flex flex-col bg-gray-50">
    <Header />
    <main class="flex-grow">
        <slot />
    </main>
    <Footer />
</body>
</html>
```

---

### 10. `src/pages/index.astro`

```astro
---
import Layout from '../layouts/Layout.astro';
import Hero from '../components/Hero.astro';
import ProductCard from '../components/ProductCard.astro';

// Images placeholder pour les produits
const placeholderImages = [
    "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&q=80",
    "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&q=80",
    "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=400&q=80",
    "https://images.unsplash.com/photo-1511920170033-f8396924c348?w=400&q=80",
];

function getImage(index: number): string {
    return placeholderImages[index % placeholderImages.length];
}
---

<Layout title="Accueil">
    <Hero />

    <!-- Section Produits en vedette -->
    <section class="py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-gray-900">Nos cafes en vedette</h2>
                <p class="text-gray-600 mt-2">Selection de nos meilleurs cafes</p>
            </div>

            <div id="featured-products" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- Charge par JavaScript -->
                <div class="col-span-full text-center py-12 text-gray-500">
                    Chargement des produits...
                </div>
            </div>

            <div class="text-center mt-10">
                <a href="/produits" class="btn-secondary">
                    Voir tous les cafes
                </a>
            </div>
        </div>
    </section>

    <!-- Section Avantages -->
    <section class="py-16 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="text-center p-6">
                    <div class="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span class="text-3xl">🌍</span>
                    </div>
                    <h3 class="font-semibold text-lg mb-2">Origines selectionnees</h3>
                    <p class="text-gray-600 text-sm">Cafes provenant des meilleures plantations du monde</p>
                </div>
                <div class="text-center p-6">
                    <div class="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span class="text-3xl">🔥</span>
                    </div>
                    <h3 class="font-semibold text-lg mb-2">Torrefaction artisanale</h3>
                    <p class="text-gray-600 text-sm">Torrefie en petites quantites pour une fraicheur optimale</p>
                </div>
                <div class="text-center p-6">
                    <div class="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span class="text-3xl">🚚</span>
                    </div>
                    <h3 class="font-semibold text-lg mb-2">Livraison rapide</h3>
                    <p class="text-gray-600 text-sm">Livre chez vous en 48h</p>
                </div>
            </div>
        </div>
    </section>
</Layout>

<script>
    import { getProduits } from '../lib/api';
    import { addToCart } from '../lib/cart';

    const placeholderImages = [
        "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&q=80",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&q=80",
        "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=400&q=80",
        "https://images.unsplash.com/photo-1511920170033-f8396924c348?w=400&q=80",
    ];

    async function loadProducts() {
        const container = document.getElementById('featured-products');
        if (!container) return;

        try {
            const produits = await getProduits();
            const featured = produits.slice(0, 4);

            if (featured.length === 0) {
                container.innerHTML = '<div class="col-span-full text-center py-12 text-gray-500">Aucun produit disponible</div>';
                return;
            }

            container.innerHTML = featured.map((p, i) => `
                <div class="product-card bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100">
                    <a href="/produit/${p.id}">
                        <div class="aspect-square overflow-hidden">
                            <img
                                src="${placeholderImages[i % placeholderImages.length]}"
                                alt="${p.nom}"
                                class="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                            />
                        </div>
                    </a>
                    <div class="p-4">
                        <a href="/produit/${p.id}">
                            <h3 class="font-semibold text-gray-900 hover:text-amber-600 transition">${p.nom}</h3>
                        </a>
                        ${p.origine ? `<p class="text-sm text-gray-500 mt-1">Origine : ${p.origine}</p>` : ''}
                        <div class="flex items-center justify-between mt-3">
                            <span class="text-lg font-bold text-amber-600">${p.prix.toFixed(2)} €</span>
                            <button
                                class="add-to-cart bg-amber-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-amber-700 transition"
                                data-id="${p.id}"
                                data-nom="${p.nom}"
                                data-prix="${p.prix}"
                            >
                                Ajouter
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');

            // Event listeners
            container.querySelectorAll('.add-to-cart').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const target = e.currentTarget as HTMLElement;
                    addToCart({
                        produit_id: parseInt(target.dataset.id!),
                        nom: target.dataset.nom!,
                        prix: parseFloat(target.dataset.prix!)
                    });
                    target.textContent = 'Ajoute !';
                    target.classList.add('bg-green-600');
                    setTimeout(() => {
                        target.textContent = 'Ajouter';
                        target.classList.remove('bg-green-600');
                    }, 1000);
                });
            });

        } catch (error) {
            container.innerHTML = '<div class="col-span-full text-center py-12 text-red-500">Erreur de chargement</div>';
        }
    }

    loadProducts();
</script>
```

---

### 11. `src/pages/produits.astro`

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Nos Cafes">
    <!-- Header de la page -->
    <section class="bg-amber-900 text-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 class="text-3xl font-bold">Nos Cafes</h1>
            <p class="text-amber-200 mt-2">Decouvrez notre selection de cafes d'exception</p>
        </div>
    </section>

    <!-- Liste des produits -->
    <section class="py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div id="products-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="col-span-full text-center py-12 text-gray-500">
                    Chargement des produits...
                </div>
            </div>
        </div>
    </section>
</Layout>

<script>
    import { getProduits } from '../lib/api';
    import { addToCart } from '../lib/cart';

    const placeholderImages = [
        "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&q=80",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&q=80",
        "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=400&q=80",
        "https://images.unsplash.com/photo-1511920170033-f8396924c348?w=400&q=80",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80",
        "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&q=80",
    ];

    async function loadProducts() {
        const container = document.getElementById('products-grid');
        if (!container) return;

        try {
            const produits = await getProduits();

            if (produits.length === 0) {
                container.innerHTML = '<div class="col-span-full text-center py-12 text-gray-500">Aucun produit disponible</div>';
                return;
            }

            container.innerHTML = produits.map((p, i) => `
                <div class="product-card bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100 fade-in">
                    <a href="/produit/${p.id}">
                        <div class="aspect-square overflow-hidden">
                            <img
                                src="${placeholderImages[i % placeholderImages.length]}"
                                alt="${p.nom}"
                                class="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                            />
                        </div>
                    </a>
                    <div class="p-4">
                        <a href="/produit/${p.id}">
                            <h3 class="font-semibold text-gray-900 hover:text-amber-600 transition">${p.nom}</h3>
                        </a>
                        ${p.origine ? `<p class="text-sm text-gray-500 mt-1">Origine : ${p.origine}</p>` : ''}
                        <p class="text-sm text-gray-500">Stock : ${p.stock}</p>
                        <div class="flex items-center justify-between mt-3">
                            <span class="text-lg font-bold text-amber-600">${p.prix.toFixed(2)} €</span>
                            <button
                                class="add-to-cart bg-amber-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-amber-700 transition"
                                data-id="${p.id}"
                                data-nom="${p.nom}"
                                data-prix="${p.prix}"
                            >
                                Ajouter
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');

            // Event listeners
            container.querySelectorAll('.add-to-cart').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const target = e.currentTarget as HTMLElement;
                    addToCart({
                        produit_id: parseInt(target.dataset.id!),
                        nom: target.dataset.nom!,
                        prix: parseFloat(target.dataset.prix!)
                    });
                    target.textContent = 'Ajoute !';
                    target.classList.add('bg-green-600');
                    setTimeout(() => {
                        target.textContent = 'Ajouter';
                        target.classList.remove('bg-green-600');
                    }, 1000);
                });
            });

        } catch (error) {
            container.innerHTML = '<div class="col-span-full text-center py-12 text-red-500">Erreur de chargement des produits</div>';
        }
    }

    loadProducts();
</script>
```

---

### 12. `src/pages/produit/[id].astro`

```astro
---
import Layout from '../../layouts/Layout.astro';

// Cette page utilise le routing dynamique
// [id] sera remplace par l'ID du produit
const { id } = Astro.params;
---

<Layout title="Detail produit">
    <section class="py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div id="product-detail" class="grid md:grid-cols-2 gap-12" data-id={id}>
                <div class="text-center py-12 text-gray-500 md:col-span-2">
                    Chargement du produit...
                </div>
            </div>
        </div>
    </section>
</Layout>

<script>
    import { getProduit } from '../../lib/api';
    import { addToCart } from '../../lib/cart';

    const placeholderImages = [
        "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&q=80",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&q=80",
        "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=800&q=80",
        "https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800&q=80",
    ];

    async function loadProduct() {
        const container = document.getElementById('product-detail');
        if (!container) return;

        const id = parseInt(container.dataset.id || '0');
        if (!id) {
            container.innerHTML = '<div class="text-center py-12 text-red-500 md:col-span-2">Produit non trouve</div>';
            return;
        }

        try {
            const p = await getProduit(id);
            const image = placeholderImages[id % placeholderImages.length];

            container.innerHTML = `
                <!-- Image -->
                <div class="aspect-square rounded-2xl overflow-hidden bg-gray-100">
                    <img src="${image}" alt="${p.nom}" class="w-full h-full object-cover" />
                </div>

                <!-- Infos -->
                <div class="flex flex-col justify-center">
                    <nav class="text-sm text-gray-500 mb-4">
                        <a href="/" class="hover:text-amber-600">Accueil</a>
                        <span class="mx-2">/</span>
                        <a href="/produits" class="hover:text-amber-600">Nos Cafes</a>
                        <span class="mx-2">/</span>
                        <span>${p.nom}</span>
                    </nav>

                    <h1 class="text-3xl font-bold text-gray-900 mb-2">${p.nom}</h1>

                    ${p.origine ? `<p class="text-gray-600 mb-4">Origine : <span class="font-medium">${p.origine}</span></p>` : ''}

                    ${p.description ? `<p class="text-gray-600 mb-6">${p.description}</p>` : '<p class="text-gray-600 mb-6">Un cafe d\'exception aux aromes subtils et complexes.</p>'}

                    <div class="flex items-center gap-4 mb-6">
                        <span class="text-3xl font-bold text-amber-600">${p.prix.toFixed(2)} €</span>
                        <span class="text-sm text-gray-500">/ ${p.poids_kg} kg</span>
                    </div>

                    <p class="text-sm ${p.stock > 0 ? 'text-green-600' : 'text-red-600'} mb-6">
                        ${p.stock > 0 ? `En stock (${p.stock} disponibles)` : 'Rupture de stock'}
                    </p>

                    <div class="flex items-center gap-4">
                        <div class="flex items-center border rounded-lg">
                            <button id="btn-minus" class="px-4 py-2 text-gray-600 hover:bg-gray-100">-</button>
                            <input id="quantity" type="number" value="1" min="1" max="${p.stock}"
                                   class="w-16 text-center border-0 focus:ring-0" />
                            <button id="btn-plus" class="px-4 py-2 text-gray-600 hover:bg-gray-100">+</button>
                        </div>
                        <button
                            id="add-to-cart"
                            class="flex-1 btn-primary ${p.stock === 0 ? 'opacity-50 cursor-not-allowed' : ''}"
                            ${p.stock === 0 ? 'disabled' : ''}
                            data-id="${p.id}"
                            data-nom="${p.nom}"
                            data-prix="${p.prix}"
                        >
                            Ajouter au panier
                        </button>
                    </div>
                </div>
            `;

            // Gestion quantite
            const qtyInput = document.getElementById('quantity') as HTMLInputElement;
            const btnMinus = document.getElementById('btn-minus');
            const btnPlus = document.getElementById('btn-plus');
            const btnAdd = document.getElementById('add-to-cart');

            btnMinus?.addEventListener('click', () => {
                const val = parseInt(qtyInput.value);
                if (val > 1) qtyInput.value = String(val - 1);
            });

            btnPlus?.addEventListener('click', () => {
                const val = parseInt(qtyInput.value);
                if (val < p.stock) qtyInput.value = String(val + 1);
            });

            btnAdd?.addEventListener('click', () => {
                const qty = parseInt(qtyInput.value);
                addToCart({
                    produit_id: p.id,
                    nom: p.nom,
                    prix: p.prix,
                    image: image
                }, qty);

                if (btnAdd) {
                    btnAdd.textContent = 'Ajoute au panier !';
                    btnAdd.classList.add('bg-green-600');
                    setTimeout(() => {
                        btnAdd.textContent = 'Ajouter au panier';
                        btnAdd.classList.remove('bg-green-600');
                    }, 1500);
                }
            });

        } catch (error) {
            container.innerHTML = '<div class="text-center py-12 text-red-500 md:col-span-2">Erreur de chargement du produit</div>';
        }
    }

    loadProduct();
</script>
```

---

### 13. `src/pages/panier.astro`

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Panier">
    <section class="py-12">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-8">Mon panier</h1>

            <div id="cart-container">
                <!-- Charge par JavaScript -->
            </div>
        </div>
    </section>
</Layout>

<script>
    import { getCart, updateQuantity, removeFromCart, clearCart, getCartTotal } from '../lib/cart';
    import { getUser } from '../lib/auth';
    import { createCommande, type LigneCommandeCreate } from '../lib/api';

    function renderCart() {
        const container = document.getElementById('cart-container');
        if (!container) return;

        const cart = getCart();

        if (cart.length === 0) {
            container.innerHTML = `
                <div class="text-center py-16">
                    <p class="text-gray-500 text-lg mb-4">Votre panier est vide</p>
                    <a href="/produits" class="btn-primary inline-block">Decouvrir nos cafes</a>
                </div>
            `;
            return;
        }

        const total = getCartTotal();

        container.innerHTML = `
            <div class="bg-white rounded-2xl shadow-sm border overflow-hidden">
                <!-- Liste des articles -->
                <div class="divide-y">
                    ${cart.map(item => `
                        <div class="p-6 flex items-center gap-6" data-item="${item.produit_id}">
                            <div class="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                                <img src="${item.image || 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=200&q=80'}"
                                     alt="${item.nom}" class="w-full h-full object-cover" />
                            </div>
                            <div class="flex-grow">
                                <h3 class="font-semibold text-gray-900">${item.nom}</h3>
                                <p class="text-amber-600 font-medium">${item.prix.toFixed(2)} €</p>
                            </div>
                            <div class="flex items-center gap-2">
                                <button class="qty-minus w-8 h-8 rounded-full border flex items-center justify-center hover:bg-gray-100">-</button>
                                <span class="w-8 text-center">${item.quantite}</span>
                                <button class="qty-plus w-8 h-8 rounded-full border flex items-center justify-center hover:bg-gray-100">+</button>
                            </div>
                            <div class="text-right">
                                <p class="font-semibold">${(item.prix * item.quantite).toFixed(2)} €</p>
                                <button class="remove-item text-sm text-red-600 hover:text-red-800">Supprimer</button>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Total et actions -->
                <div class="bg-gray-50 p-6">
                    <div class="flex justify-between items-center mb-6">
                        <span class="text-lg font-medium">Total</span>
                        <span class="text-2xl font-bold text-amber-600">${total.toFixed(2)} €</span>
                    </div>
                    <div class="flex gap-4">
                        <button id="clear-cart" class="px-4 py-2 text-gray-600 border rounded-lg hover:bg-gray-100 transition">
                            Vider le panier
                        </button>
                        <button id="checkout" class="flex-1 btn-primary">
                            Passer commande
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Event listeners
        container.querySelectorAll('.qty-minus').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = (e.target as HTMLElement).closest('[data-item]') as HTMLElement;
                const id = parseInt(item.dataset.item!);
                const current = cart.find(i => i.produit_id === id);
                if (current && current.quantite > 1) {
                    updateQuantity(id, current.quantite - 1);
                    renderCart();
                }
            });
        });

        container.querySelectorAll('.qty-plus').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = (e.target as HTMLElement).closest('[data-item]') as HTMLElement;
                const id = parseInt(item.dataset.item!);
                const current = cart.find(i => i.produit_id === id);
                if (current) {
                    updateQuantity(id, current.quantite + 1);
                    renderCart();
                }
            });
        });

        container.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = (e.target as HTMLElement).closest('[data-item]') as HTMLElement;
                const id = parseInt(item.dataset.item!);
                removeFromCart(id);
                renderCart();
            });
        });

        document.getElementById('clear-cart')?.addEventListener('click', () => {
            if (confirm('Vider le panier ?')) {
                clearCart();
                renderCart();
            }
        });

        document.getElementById('checkout')?.addEventListener('click', async () => {
            const user = getUser();
            if (!user) {
                alert('Veuillez vous connecter pour passer commande');
                window.location.href = '/connexion';
                return;
            }

            const cart = getCart();
            const lignes: LigneCommandeCreate[] = cart.map(item => ({
                produit_id: item.produit_id,
                quantite: item.quantite,
                prix_unitaire: item.prix
            }));

            try {
                await createCommande({
                    client_id: user.id,
                    lignes
                });
                clearCart();
                alert('Commande passee avec succes !');
                window.location.href = '/compte';
            } catch (error) {
                alert('Erreur lors de la commande. Veuillez reessayer.');
            }
        });
    }

    renderCart();
    window.addEventListener('cart-updated', renderCart);
</script>
```

---

### 14. `src/pages/connexion.astro`

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Connexion">
    <section class="py-16">
        <div class="max-w-md mx-auto px-4">
            <div class="bg-white rounded-2xl shadow-sm border p-8">
                <h1 class="text-2xl font-bold text-center mb-8">Connexion</h1>

                <form id="login-form" class="space-y-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                        <input
                            type="email"
                            id="email"
                            required
                            placeholder="votre@email.com"
                            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none"
                        />
                    </div>

                    <div id="error-message" class="text-red-600 text-sm hidden"></div>

                    <button type="submit" class="w-full btn-primary">
                        Se connecter
                    </button>
                </form>

                <p class="text-center text-gray-600 mt-6">
                    Pas encore de compte ?
                    <a href="/inscription" class="text-amber-600 hover:text-amber-700 font-medium">S'inscrire</a>
                </p>
            </div>
        </div>
    </section>
</Layout>

<script>
    import { login } from '../lib/auth';

    const form = document.getElementById('login-form') as HTMLFormElement;
    const errorDiv = document.getElementById('error-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = (document.getElementById('email') as HTMLInputElement).value;

        try {
            await login(email);
            window.location.href = '/compte';
        } catch (error) {
            if (errorDiv) {
                errorDiv.textContent = (error as Error).message;
                errorDiv.classList.remove('hidden');
            }
        }
    });
</script>
```

---

### 15. `src/pages/inscription.astro`

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Inscription">
    <section class="py-16">
        <div class="max-w-md mx-auto px-4">
            <div class="bg-white rounded-2xl shadow-sm border p-8">
                <h1 class="text-2xl font-bold text-center mb-8">Creer un compte</h1>

                <form id="register-form" class="space-y-6">
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Nom</label>
                            <input
                                type="text"
                                id="nom"
                                required
                                class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none"
                            />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Prenom</label>
                            <input
                                type="text"
                                id="prenom"
                                required
                                class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none"
                            />
                        </div>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                        <input
                            type="email"
                            id="email"
                            required
                            placeholder="votre@email.com"
                            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none"
                        />
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Telephone (optionnel)</label>
                        <input
                            type="tel"
                            id="telephone"
                            placeholder="06 12 34 56 78"
                            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none"
                        />
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Adresse (optionnel)</label>
                        <input
                            type="text"
                            id="adresse"
                            placeholder="123 Rue du Cafe, Paris"
                            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none"
                        />
                    </div>

                    <div id="error-message" class="text-red-600 text-sm hidden"></div>

                    <button type="submit" class="w-full btn-primary">
                        Creer mon compte
                    </button>
                </form>

                <p class="text-center text-gray-600 mt-6">
                    Deja un compte ?
                    <a href="/connexion" class="text-amber-600 hover:text-amber-700 font-medium">Se connecter</a>
                </p>
            </div>
        </div>
    </section>
</Layout>

<script>
    import { register } from '../lib/auth';

    const form = document.getElementById('register-form') as HTMLFormElement;
    const errorDiv = document.getElementById('error-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            nom: (document.getElementById('nom') as HTMLInputElement).value,
            prenom: (document.getElementById('prenom') as HTMLInputElement).value,
            email: (document.getElementById('email') as HTMLInputElement).value,
            telephone: (document.getElementById('telephone') as HTMLInputElement).value || undefined,
            adresse: (document.getElementById('adresse') as HTMLInputElement).value || undefined
        };

        try {
            await register(data);
            window.location.href = '/compte';
        } catch (error) {
            if (errorDiv) {
                errorDiv.textContent = (error as Error).message;
                errorDiv.classList.remove('hidden');
            }
        }
    });
</script>
```

---

### 16. `src/pages/compte.astro`

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Mon compte">
    <section class="py-12">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div id="account-container">
                <!-- Charge par JavaScript -->
                <div class="text-center py-12 text-gray-500">Chargement...</div>
            </div>
        </div>
    </section>
</Layout>

<script>
    import { getUser, logout } from '../lib/auth';
    import { getCommandesByClient } from '../lib/api';

    async function loadAccount() {
        const container = document.getElementById('account-container');
        if (!container) return;

        const user = getUser();

        if (!user) {
            window.location.href = '/connexion';
            return;
        }

        // Charger les commandes
        let commandes: any[] = [];
        try {
            commandes = await getCommandesByClient(user.id);
        } catch (error) {
            console.error('Erreur chargement commandes:', error);
        }

        const statusColors: Record<string, string> = {
            'en_attente': 'bg-yellow-100 text-yellow-800',
            'validee': 'bg-green-100 text-green-800',
            'en_preparation': 'bg-blue-100 text-blue-800',
            'expediee': 'bg-purple-100 text-purple-800',
            'livree': 'bg-green-100 text-green-800',
            'annulee': 'bg-red-100 text-red-800'
        };

        container.innerHTML = `
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900">Bonjour, ${user.prenom} !</h1>
                <p class="text-gray-600 mt-1">${user.email}</p>
            </div>

            <!-- Infos compte -->
            <div class="bg-white rounded-2xl shadow-sm border p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">Mes informations</h2>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="text-gray-500">Nom :</span>
                        <span class="font-medium ml-2">${user.nom}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Prenom :</span>
                        <span class="font-medium ml-2">${user.prenom}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Email :</span>
                        <span class="font-medium ml-2">${user.email}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Telephone :</span>
                        <span class="font-medium ml-2">${user.telephone || '-'}</span>
                    </div>
                    <div class="col-span-2">
                        <span class="text-gray-500">Adresse :</span>
                        <span class="font-medium ml-2">${user.adresse || '-'}</span>
                    </div>
                </div>
            </div>

            <!-- Commandes -->
            <div class="bg-white rounded-2xl shadow-sm border overflow-hidden">
                <div class="p-6 border-b">
                    <h2 class="text-xl font-semibold">Mes commandes</h2>
                </div>

                ${commandes.length === 0 ? `
                    <div class="p-12 text-center text-gray-500">
                        <p>Vous n'avez pas encore passe de commande</p>
                        <a href="/produits" class="btn-primary inline-block mt-4">Decouvrir nos cafes</a>
                    </div>
                ` : `
                    <div class="divide-y">
                        ${commandes.map(cmd => `
                            <div class="p-6">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="font-semibold">Commande #${cmd.id}</span>
                                    <span class="px-3 py-1 rounded-full text-xs font-medium ${statusColors[cmd.statut] || 'bg-gray-100'}">
                                        ${cmd.statut}
                                    </span>
                                </div>
                                <div class="text-sm text-gray-600 mb-2">
                                    ${new Date(cmd.date_commande).toLocaleDateString('fr-FR', {
                                        day: 'numeric',
                                        month: 'long',
                                        year: 'numeric'
                                    })}
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-500">${cmd.lignes.length} article(s)</span>
                                    <span class="font-bold text-amber-600">${cmd.total.toFixed(2)} €</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `}
            </div>

            <!-- Deconnexion -->
            <div class="mt-8 text-center">
                <button id="btn-logout" class="text-red-600 hover:text-red-800 font-medium">
                    Se deconnecter
                </button>
            </div>
        `;

        document.getElementById('btn-logout')?.addEventListener('click', () => {
            logout();
            window.location.href = '/';
        });
    }

    loadAccount();
</script>
```

---

### 17. `public/favicon.svg`

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <text y=".9em" font-size="90">☕</text>
</svg>
```

---

## LANCER LE PROJET

### 1. Installer les dependances

```bash
cd /Users/faouzdon/Desktop/payetonkawa/sitepayetonkawa
npm install
```

### 2. Lancer le serveur de developpement

```bash
npm run dev
```

Le site sera accessible sur **http://localhost:4321**

### 3. Build pour la production

```bash
npm run build
```

---

## RAPPEL : ACTIVER LE CORS

Avant de lancer le site, il faut activer le CORS dans les 3 APIs.

Dans chaque `main.py` (api-clients, api-produits, api-commandes) :

```python
from fastapi.middleware.cors import CORSMiddleware

# Apres app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Puis relancer Docker :

```bash
cd /Users/faouzdon/Desktop/payetonkawa
docker compose down && docker compose up -d --build
```

---

## RESUME

| Page | URL | Description |
|------|-----|-------------|
| Accueil | `/` | Banniere + produits en vedette |
| Catalogue | `/produits` | Liste de tous les produits |
| Detail | `/produit/[id]` | Page d'un produit |
| Panier | `/panier` | Gestion du panier |
| Connexion | `/connexion` | Se connecter |
| Inscription | `/inscription` | Creer un compte |
| Compte | `/compte` | Profil + commandes |
