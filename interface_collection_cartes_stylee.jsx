import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";

export default function App() {
  const [cards, setCards] = useState([]);
  const [name, setName] = useState("");
  const [set, setSet] = useState("");
  const [price, setPrice] = useState("");

  const addCard = () => {
    if (!name) return;
    setCards([...cards, { name, set, price }]);
    setName("");
    setSet("");
    setPrice("");
  };

  const removeCard = (index) => {
    setCards(cards.filter((_, i) => i !== index));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-black text-white p-6">
      <h1 className="text-4xl font-bold mb-6 text-center">Ma Collection</h1>

      <div className="grid md:grid-cols-4 gap-4 mb-6">
        <Input placeholder="Nom" value={name} onChange={(e) => setName(e.target.value)} />
        <Input placeholder="Extension" value={set} onChange={(e) => setSet(e.target.value)} />
        <Input placeholder="Prix" value={price} onChange={(e) => setPrice(e.target.value)} />
        <Button onClick={addCard}>Ajouter</Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {cards.map((card, index) => (
          <motion.div key={index} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl shadow-lg">
              <CardContent className="p-4">
                <h2 className="text-xl font-semibold">{card.name}</h2>
                <p className="text-sm opacity-70">{card.set}</p>
                <p className="mt-2 font-bold">{card.price} €</p>
                <Button variant="destructive" className="mt-3 w-full" onClick={() => removeCard(index)}>
                  Supprimer
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
