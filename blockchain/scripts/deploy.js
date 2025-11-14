const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying ProofOfPresence contract...");

  const ProofOfPresence = await ethers.getContractFactory("ProofOfPresence");
  const pop = await ProofOfPresence.deploy();
  await pop.waitForDeployment();

  const address = await pop.getAddress();
  console.log("✅ Contract deployed to:", address);

  // Crear objeto con la info del contrato
  const contractData = {
    address,
    abi: JSON.parse(pop.interface.formatJson()),
  };

  // Guardar en carpeta /deployed
  const dir = path.resolve(__dirname, "../deployed");
  const filePath = path.join(dir, "ProofOfPresence.json");

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
  }

  fs.writeFileSync(filePath, JSON.stringify(contractData, null, 2));
  console.log("📄 Contract info saved to:", filePath);
}

main().catch((error) => {
  console.error("❌ Error deploying contract:", error);
  process.exitCode = 1;
});
