async function main() {
  // Importamos el entorno dinámicamente desde Hardhat
  const hre = require("hardhat");

  // Confirmamos que ethers está disponible
  const { ethers } = hre;

  // Obtenemos el contrato
  const ProofOfPresence = await ethers.getContractFactory("ProofOfPresence");

  // Lo desplegamos
  const pop = await ProofOfPresence.deploy();

  // Esperamos a que esté en la red
  await pop.waitForDeployment();

  console.log("✅ Contract deployed to:", await pop.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error:", error);
    process.exit(1);
  });
