/**
 * GESTION DU PANIER
 * Stocke dans localStorage.
 */

const CART_KEY = 'payetonkawa_cart';

export interface CartItem {
    produit_id: number;
    nom: string;
    prix: number;
    quantite: number;
    image?: string;
}

export function getCart(): CartItem[] {
    if (typeof window === 'undefined') return [];

    const stored = localStorage.getItem(CART_KEY);
    if (!stored) return [];

    try {
        return JSON.parse(stored);
    } catch {
        return [];
    }
}

function saveCart(cart: CartItem[]): void {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    window.dispatchEvent(new CustomEvent('cart-updated', { detail: cart }));
}

export function addToCart(item: Omit<CartItem, 'quantite'>, quantite: number = 1): void {
    const cart = getCart();
    const existingIndex = cart.findIndex(i => i.produit_id === item.produit_id);

    if (existingIndex !== -1) {
        cart[existingIndex].quantite += quantite;
    } else {
        cart.push({ ...item, quantite });
    }

    saveCart(cart);
}

export function updateQuantity(produit_id: number, quantite: number): void {
    let cart = getCart();

    if (quantite <= 0) {
        cart = cart.filter(i => i.produit_id !== produit_id);
    } else {
        const item = cart.find(i => i.produit_id === produit_id);
        if (item) {
            item.quantite = quantite;
        }
    }

    saveCart(cart);
}

export function removeFromCart(produit_id: number): void {
    const cart = getCart().filter(i => i.produit_id !== produit_id);
    saveCart(cart);
}

export function clearCart(): void {
    saveCart([]);
}

export function getCartCount(): number {
    return getCart().reduce((sum, item) => sum + item.quantite, 0);
}

export function getCartTotal(): number {
    return getCart().reduce((sum, item) => sum + (item.prix * item.quantite), 0);
}
