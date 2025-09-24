import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import QuoteGenerator from "./components/QuoteGenerator";
import { Toaster } from "./components/ui/sonner";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<QuoteGenerator />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;
