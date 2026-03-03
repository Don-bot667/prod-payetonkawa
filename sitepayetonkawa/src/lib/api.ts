// Configuration des APIs
const API_CLIENTS = "https://api.payetonkawa.ouzfa.com";
const API_PRODUITS = "https://api.payetonkawa.ouzfa.com";
const API_COMMANDES = "https://api.payetonkawa.ouzfa.com";

// Clé API envoyée dans chaque requête
const API_KEY = "secret_key_123";

// Headers communs à toutes les requêtes
const HEADERS_JSON = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
};

const HEADERS_GET = {
    "X-API-Key": API_KEY
};

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
    mot_de_passe: string;
}

export interface Produit {
    id: number;
    nom: string;
    description?: string;
    prix: number;
    stock: number;
    poids_kg: number;
    origine?: string;
    image_url?: string;
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
    const response = await fetch(`${API_CLIENTS}/customers/`, {
        headers: HEADERS_GET
    });
    if (!response.ok) throw new Error("Erreur API Clients");
    return response.json();
}

export async function getClient(id: number): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/${id}`, {
        headers: HEADERS_GET
    });
    if (!response.ok) throw new Error("Client non trouve");
    return response.json();
}

export async function createClient(data: ClientCreate): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/`, {
        method: "POST",
        headers: HEADERS_JSON,
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error("Erreur creation client");
    return response.json();
}

export async function loginClient(email: string, mot_de_passe: string): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/login`, {
        method: "POST",
        headers: HEADERS_JSON,
        body: JSON.stringify({ email, mot_de_passe })
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Email ou mot de passe incorrect");
    }
    return response.json();
}

// ============ HELPERS ============

export function getImageUrl(imageUrl: string | null | undefined): string {
    if (!imageUrl) return '';
    return `${API_PRODUITS}/products${imageUrl}`;
}

// ============ PRODUITS ============

export async function getProduits(): Promise<Produit[]> {
    const response = await fetch(`${API_PRODUITS}/products/`, {
        headers: HEADERS_GET
    });
    if (!response.ok) throw new Error("Erreur API Produits");
    return response.json();
}

export async function getProduit(id: number): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/${id}`, {
        headers: HEADERS_GET
    });
    if (!response.ok) throw new Error("Produit non trouve");
    return response.json();
}

// ============ COMMANDES ============

export async function getCommandes(): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/`, {
        headers: HEADERS_GET
    });
    if (!response.ok) throw new Error("Erreur API Commandes");
    return response.json();
}

export async function getCommandesByClient(clientId: number): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/client/${clientId}`, {
        headers: HEADERS_GET
    });
    if (!response.ok) throw new Error("Erreur recuperation commandes");
    return response.json();
}

export async function createCommande(data: CommandeCreate): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/`, {
        method: "POST",
        headers: HEADERS_JSON,
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error("Erreur creation commande");
    return response.json();
}
