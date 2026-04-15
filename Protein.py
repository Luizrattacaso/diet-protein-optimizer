class Protein:
    def __init__(self, name, price, grams, protein_grams):
        self.name = name
        self.price = price
        self.grams = grams
        self.protein_grams = protein_grams  #proteina/g

    def get_price(self):
        return self.price

    def get_grams(self):
        return self.grams

    def get_protein(self):
        return self.protein_grams

    def price_per_gram(self):
        return self.price / self.grams if self.grams > 0 else float('inf')

    def protein_density(self):
        return self.protein_grams / self.grams if self.grams > 0 else 0.0

    def __repr__(self):
        return f"{self.name} | {self.grams}g | R${self.price:.2f} | {self.protein_grams}g prot"