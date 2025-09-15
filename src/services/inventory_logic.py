from datetime import date


class InventoryError(ValueError):
    pass


def validate_new_product(name: str, quantity: float, expiry_date: date) -> None:
    if not name or name.strip() == "":
        raise InventoryError("Le nom du produit est obligatoire.")
    if quantity is None or quantity <= 0:
        raise InventoryError("La quantité doit être > 0.")
    if expiry_date is None:
        raise InventoryError("La date de péremption est obligatoire.")


def normalize_name(name: str) -> str:
    # Normalisation simple : trim + minuscules
    return " ".join(name.strip().split()).lower()
