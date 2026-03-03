/**
 * AUTHENTIFICATION SIMPLIFIEE
 * Les donnees sont stockees dans localStorage.
 */

import { loginClient, createClient, type Client, type ClientCreate } from './api';

const STORAGE_KEY = 'payetonkawa_user';

export function getUser(): Client | null {
    if (typeof window === 'undefined') return null;

    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    try {
        return JSON.parse(stored);
    } catch {
        return null;
    }
}

export function isLoggedIn(): boolean {
    return getUser() !== null;
}

export async function login(email: string, mot_de_passe: string): Promise<Client> {
    const client = await loginClient(email, mot_de_passe);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(client));
    return client;
}

export async function register(data: ClientCreate): Promise<Client> {
    const newClient = await createClient(data);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newClient));
    return newClient;
}

export function logout(): void {
    localStorage.removeItem(STORAGE_KEY);
}
