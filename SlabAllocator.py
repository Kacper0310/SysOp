class Slab:
    def __init__(self, object_size, objects_per_slab):
        self.object_size = object_size
        self.objects_per_slab = objects_per_slab
        # Symulacja ciągłego bloku pamięci
        self.memory = [None] * objects_per_slab 
        # Mapa bitowa: False = wolne, True = zajęte
        self.bitmap = [False] * objects_per_slab

    def alloc(self):
        for i in range(self.objects_per_slab):
            if not self.bitmap[i]:
                self.bitmap[i] = True
                # Zwracamy "adres" jako krotkę (id_slaba, indeks)
                return i
        return None

    def free(self, index):
        if 0 <= index < self.objects_per_slab:
            self.bitmap[index] = False
            return True
        return False

    def is_full(self):
        return all(self.bitmap)

    def is_empty(self):
        return not any(self.bitmap)
    
class SlabCache:
    def __init__(self, object_size, objects_per_slab):
        self.object_size = object_size
        self.objects_per_slab = objects_per_slab
        self.slabs = []

    def alloc(self):
        # 1. Szukaj miejsca w istniejących slabach
        for slab_idx, slab in enumerate(self.slabs):
            obj_idx = slab.alloc()
            if obj_idx is not None:
                print(f"[Alloc] Znaleziono miejsce w Slab {slab_idx}, pozycja {obj_idx}")
                return (slab_idx, obj_idx)

        # 2. Brak miejsca - stwórz nowy slab
        print(f"[Alloc] Brak miejsca. Tworzenie Slab {len(self.slabs)}")
        new_slab = Slab(self.object_size, self.objects_per_slab)
        self.slabs.append(new_slab)
        obj_idx = new_slab.alloc()
        return (len(self.slabs) - 1, obj_idx)

    def free(self, address):
        slab_idx, obj_idx = address
        if 0 <= slab_idx < len(self.slabs):
            if self.slabs[slab_idx].free(obj_idx):
                print(f"[Free] Zwolniono Slab {slab_idx}, pozycja {obj_idx}")
                # Opcjonalnie: usuń pusty slab, jeśli nie jest jedynym
                if self.slabs[slab_idx].is_empty() and len(self.slabs) > 1:
                    print(f"[Cache] Usuwanie pustego Slab {slab_idx}")
                    self.slabs.pop(slab_idx)
                return
        print("[Error] Nieprawidłowy adres do zwolnienia")

# Konfiguracja: Obiekty 16-bajtowe, po 3 na każdy Slab
cache = SlabCache(object_size=16, objects_per_slab=3)

print("--- Faza 1: Alokacja 3 obiektów (Zapełnienie Slab 0) ---")
addr1 = cache.alloc()
addr2 = cache.alloc()
addr3 = cache.alloc()

print("\n--- Faza 2: Alokacja 4-tego obiektu (Nowy Slab 1) ---")
addr4 = cache.alloc()

print("\n--- Faza 3: Zwolnienie obiektu ze środka Slab 0 i ponowna alokacja ---")
cache.free(addr2)
addr5 = cache.alloc() # Powinien trafić w miejsce addr2

print("\n--- Faza 4: Sprzątanie ---")
cache.free(addr1)
cache.free(addr3)
cache.free(addr4)
cache.free(addr5)