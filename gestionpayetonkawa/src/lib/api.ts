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

// --- TYPES ---

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

export interface ProduitCreate {
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

// --- CLIENTS ---

export async function getClients(): Promise<Client[]> {
    const response = await fetch(`${API_CLIENTS}/customers/`, {
        headers: HEADERS_GET
    });
    return await response.json();
}

export async function getClient(id: number): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/${id}`, {
        headers: HEADERS_GET
    });
    return await response.json();
}

export async function createClient(data: ClientCreate): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/`, {
        method: "POST",
        headers: HEADERS_JSON,
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function deleteClient(id: number): Promise<void> {
    await fetch(`${API_CLIENTS}/customers/${id}`, {
        method: "DELETE",
        headers: HEADERS_GET
    });
}

// --- PRODUITS ---

export async function getProduits(): Promise<Produit[]> {
    const response = await fetch(`${API_PRODUITS}/products/`, {
        headers: HEADERS_GET
    });
    return await response.json();
}

export async function getProduit(id: number): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/${id}`, {
        headers: HEADERS_GET
    });
    return await response.json();
}

export async function createProduit(data: ProduitCreate): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/`, {
        method: "POST",
        headers: HEADERS_JSON,
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function updateProduit(id: number, data: Partial<ProduitCreate>): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/${id}`, {
        method: "PUT",
        headers: HEADERS_JSON,
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function deleteProduit(id: number): Promise<void> {
    await fetch(`${API_PRODUITS}/products/${id}`, {
        method: "DELETE",
        headers: HEADERS_GET
    });
}

export async function uploadProductImage(id: number, file: File): Promise<Produit> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_PRODUITS}/products/${id}/image`, {
        method: "POST",
        headers: { "X-API-Key": API_KEY },
        body: formData
    });
    if (!response.ok) throw new Error("Erreur upload image");
    return response.json();
}

// --- COMMANDES ---

export async function getCommandes(): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/`, {
        headers: HEADERS_GET
    });
    return await response.json();
}

export async function getCommande(id: number): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/${id}`, {
        headers: HEADERS_GET
    });
    return await response.json();
}

export async function createCommande(data: CommandeCreate): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/`, {
        method: "POST",
        headers: HEADERS_JSON,
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function updateCommande(id: number, data: { statut: string }): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/${id}`, {
        method: "PUT",
        headers: HEADERS_JSON,
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function deleteCommande(id: number): Promise<void> {
    await fetch(`${API_COMMANDES}/orders/${id}`, {
        method: "DELETE",
        headers: HEADERS_GET
    });
}
