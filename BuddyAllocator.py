import math

class BuddyAllocator:
    def __init__(self, total_size, split_limit):
        # Sprawdzenie czy rozmiar jest potęgą 2
        if (total_size & (total_size - 1)) != 0:
            raise ValueError("Rozmiar pamięci musi być potęgą liczby 2.")
            
        self.total_size = total_size
        self.min_block_size = total_size // (2 ** split_limit)
        
        # Mapa wolnych bloków: {rozmiar: [adresy]}
        self.free_blocks = {total_size: [0]}
        # Śledzenie zajętych bloków (adres: rozmiar) dla bezpiecznego zwalniania
        self.allocated_blocks = {}

        print(f"Zainicjalizowano buddy allocator: Total={total_size}, MinBlock={self.min_block_size}")

    def alloc(self, size):
        if size <= 0:
            return None
        
        # 1. Wyznaczenie wymaganego rozmiaru bloku (potęga 2)
        block_size = 2 ** math.ceil(math.log2(size))
        if block_size < self.min_block_size:
            block_size = self.min_block_size
            
        print(f"Próba alokacji {size} bajtów (rozmiar bloku: {block_size})")

        # 2. Szukanie dostępnego bloku (ewentualny podział większych)
        current_size = block_size
        while current_size <= self.total_size:
            if self.free_blocks.get(current_size):
                # Znaleziono wolny blok
                address = self.free_blocks[current_size].pop(0)
                
                # 3. Rekurencyjny podział bloku (jeśli znaleziony jest większy niż wymagany)
                while current_size > block_size:
                    current_size //= 2
                    buddy_address = address + current_size
                    # Dodaj prawą połówkę do wolnych bloków
                    if current_size not in self.free_blocks:
                        self.free_blocks[current_size] = []
                    self.free_blocks[current_size].append(buddy_address)
                    print(f"  Podział bloku na adresie {address}: powstał znajomy na {buddy_address} (rozmiar {current_size})")
                
                self.allocated_blocks[address] = block_size
                return (address, block_size)
            
            current_size *= 2
            
        print("  Błąd: Brak wystarczającej pamięci.")
        return None

    def free(self, address, size):
        # Zabezpieczenie przed invalid/double free
        if address not in self.allocated_blocks or self.allocated_blocks[address] != size:
            print(f"  Błąd: Nieprawidłowe zwolnienie adresu {address} o rozmiarze {size}")
            return False

        del self.allocated_blocks[address]
        self._free_recursive(address, size)
        return True

    def _free_recursive(self, address, size):
        if size == self.total_size:
            if size not in self.free_blocks: self.free_blocks[size] = []
            self.free_blocks[size].append(address)
            return

        # Wyznaczenie adresu znajomego 
        buddy_address = address ^ size
        
        # Sprawdzenie czy znajomy jest wolny i ma ten sam rozmiar
        free_list = self.free_blocks.get(size, [])
        if buddy_address in free_list:
            print(f"  Łączenie: Blok {address} i znajomy {buddy_address} (rozmiar {size}) -> {size * 2}")
            free_list.remove(buddy_address)
            # Łączymy i próbujemy scalić wyżej
            new_address = min(address, buddy_address)
            self._free_recursive(new_address, size * 2)
        else:
            # Nie można scali dodaj do listy wolnych
            if size not in self.free_blocks:
                self.free_blocks[size] = []
            self.free_blocks[size].append(address)
            print(f"  Zwolniono blok na adresie {address} (rozmiar {size})")

    def show_state(self):
        print(f"Stan wolnych bloków: {self.free_blocks}")

allocator = BuddyAllocator(2048, 6)

#pierwsza alokacja
res1 = allocator.alloc(100) # Powinien wziąć blok 128
print(f"Alokacja 1: {res1}")

#druga alokacja 
res2 = allocator.alloc(200) # Powinien wziąć blok 256
print(f"Alokacja 2: {res2}")

#zwolnienie alokacji 
if res1:
    allocator.free(res1[0], res1[1])

allocator.show_state()