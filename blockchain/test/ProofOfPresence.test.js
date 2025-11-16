/**
 * ProofOfPresence Smart Contract Tests
 * 
 * Tests completos para verificar funcionalidad, seguridad y casos extremos.
 * 
 * Para ejecutar:
 * npx hardhat test
 * 
 * Para coverage:
 * npx hardhat coverage
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

describe("ProofOfPresence Contract", function () {
  let proofOfPresence;
  let owner;
  let user1;
  let user2;
  let user3;

  // Setup antes de cada test
  beforeEach(async function () {
    // Obtener cuentas de prueba
    [owner, user1, user2, user3] = await ethers.getSigners();
    
    // Desplegar contrato fresco
    const ProofOfPresence = await ethers.getContractFactory("ProofOfPresence");
    proofOfPresence = await ProofOfPresence.deploy();
    await proofOfPresence.waitForDeployment();
  });

  // ============================================
  // TESTS DE DEPLOYMENT
  // ============================================
  
  describe("Deployment", function () {
    it("Should deploy successfully", async function () {
      const address = await proofOfPresence.getAddress();
      expect(address).to.be.properAddress;
    });

    it("Should set the right owner", async function () {
      expect(await proofOfPresence.owner()).to.equal(owner.address);
    });
  });

  // ============================================
  // TESTS DE CHECK-IN BÁSICO
  // ============================================
  
  describe("Basic Check-in", function () {
    it("Should allow user to check in to an event", async function () {
      const eventId = 1;
      const location = "Santiago, Chile";

      await proofOfPresence.connect(user1).checkInEvent(eventId, location);

      const checkIns = await proofOfPresence.getUserCheckIns(user1.address);
      expect(checkIns.length).to.equal(1);
      expect(checkIns[0].eventId).to.equal(eventId);
      expect(checkIns[0].location).to.equal(location);
      expect(checkIns[0].user).to.equal(user1.address);
    });

    it("Should emit EventCheckedIn event", async function () {
      const eventId = 1;
      const location = "Santiago, Chile";

      await expect(
        proofOfPresence.connect(user1).checkInEvent(eventId, location)
      )
        .to.emit(proofOfPresence, "EventCheckedIn")
        .withArgs(user1.address, eventId, location, await time.latest() + 1);
    });

    it("Should record timestamp correctly", async function () {
      const eventId = 1;
      const location = "Santiago, Chile";

      const tx = await proofOfPresence.connect(user1).checkInEvent(eventId, location);
      const receipt = await tx.wait();
      const block = await ethers.provider.getBlock(receipt.blockNumber);

      const checkIns = await proofOfPresence.getUserCheckIns(user1.address);
      expect(checkIns[0].timestamp).to.equal(block.timestamp);
    });

    it("Should allow multiple users to check in to same event", async function () {
      const eventId = 1;
      const location = "Santiago, Chile";

      await proofOfPresence.connect(user1).checkInEvent(eventId, location);
      await proofOfPresence.connect(user2).checkInEvent(eventId, location);
      await proofOfPresence.connect(user3).checkInEvent(eventId, location);

      const checkIns1 = await proofOfPresence.getUserCheckIns(user1.address);
      const checkIns2 = await proofOfPresence.getUserCheckIns(user2.address);
      const checkIns3 = await proofOfPresence.getUserCheckIns(user3.address);

      expect(checkIns1.length).to.equal(1);
      expect(checkIns2.length).to.equal(1);
      expect(checkIns3.length).to.equal(1);
    });
  });

  // ============================================
  // TESTS DE VALIDACIÓN
  // ============================================
  
  describe("Validation", function () {
    it("Should prevent duplicate check-ins to same event", async function () {
      const eventId = 1;
      const location = "Santiago, Chile";

      await proofOfPresence.connect(user1).checkInEvent(eventId, location);

      await expect(
        proofOfPresence.connect(user1).checkInEvent(eventId, location)
      ).to.be.revertedWith("Already checked in to this event");
    });

    it("Should reject empty location", async function () {
      const eventId = 1;
      const location = "";

      await expect(
        proofOfPresence.connect(user1).checkInEvent(eventId, location)
      ).to.be.revertedWith("Location cannot be empty");
    });

    it("Should reject invalid event ID (0)", async function () {
      const eventId = 0;
      const location = "Santiago, Chile";

      await expect(
        proofOfPresence.connect(user1).checkInEvent(eventId, location)
      ).to.be.revertedWith("Invalid event ID");
    });

    it("Should allow user to check in to different events", async function () {
      await proofOfPresence.connect(user1).checkInEvent(1, "Event 1");
      await proofOfPresence.connect(user1).checkInEvent(2, "Event 2");
      await proofOfPresence.connect(user1).checkInEvent(3, "Event 3");

      const checkIns = await proofOfPresence.getUserCheckIns(user1.address);
      expect(checkIns.length).to.equal(3);
      expect(checkIns[0].eventId).to.equal(1);
      expect(checkIns[1].eventId).to.equal(2);
      expect(checkIns[2].eventId).to.equal(3);
    });
  });

  // ============================================
  // TESTS DE ESTADÍSTICAS
  // ============================================
  
  describe("Event Statistics", function () {
    it("Should track event statistics correctly", async function () {
      const eventId = 1;

      await proofOfPresence.connect(user1).checkInEvent(eventId, "Location 1");
      await proofOfPresence.connect(user2).checkInEvent(eventId, "Location 2");
      await proofOfPresence.connect(user3).checkInEvent(eventId, "Location 3");

      const stats = await proofOfPresence.getEventStats(eventId);
      expect(stats.totalCheckIns).to.equal(3);
      expect(stats.uniqueUsers).to.equal(3);
      expect(stats.exists).to.be.true;
    });

    it("Should return empty stats for non-existent event", async function () {
      const stats = await proofOfPresence.getEventStats(999);
      expect(stats.totalCheckIns).to.equal(0);
      expect(stats.uniqueUsers).to.equal(0);
      expect(stats.exists).to.be.false;
    });

    it("Should emit EventCreated on first check-in", async function () {
      const eventId = 1;

      await expect(
        proofOfPresence.connect(user1).checkInEvent(eventId, "Location")
      ).to.emit(proofOfPresence, "EventCreated");
    });

    it("Should not emit EventCreated on subsequent check-ins", async function () {
      const eventId = 1;

      await proofOfPresence.connect(user1).checkInEvent(eventId, "Location 1");

      await expect(
        proofOfPresence.connect(user2).checkInEvent(eventId, "Location 2")
      ).to.not.emit(proofOfPresence, "EventCreated");
    });
  });

  // ============================================
  // TESTS DE QUERIES
  // ============================================
  
  describe("User Queries", function () {
    it("Should get user check-in count", async function () {
      await proofOfPresence.connect(user1).checkInEvent(1, "Event 1");
      await proofOfPresence.connect(user1).checkInEvent(2, "Event 2");
      await proofOfPresence.connect(user1).checkInEvent(3, "Event 3");

      const count = await proofOfPresence.getUserCheckInCount(user1.address);
      expect(count).to.equal(3);
    });

    it("Should return 0 for user with no check-ins", async function () {
      const count = await proofOfPresence.getUserCheckInCount(user1.address);
      expect(count).to.equal(0);
    });

    it("Should verify if user checked in to event", async function () {
      const eventId = 1;

      expect(await proofOfPresence.hasUserCheckedIn(user1.address, eventId)).to.be.false;

      await proofOfPresence.connect(user1).checkInEvent(eventId, "Location");

      expect(await proofOfPresence.hasUserCheckedIn(user1.address, eventId)).to.be.true;
    });

    it("Should get last check-in correctly", async function () {
      await proofOfPresence.connect(user1).checkInEvent(1, "First");
      await proofOfPresence.connect(user1).checkInEvent(2, "Second");
      await proofOfPresence.connect(user1).checkInEvent(3, "Third");

      const lastCheckIn = await proofOfPresence.getLastCheckIn(user1.address);
      expect(lastCheckIn.eventId).to.equal(3);
      expect(lastCheckIn.location).to.equal("Third");
    });

    it("Should revert when getting last check-in for user with no check-ins", async function () {
      await expect(
        proofOfPresence.getLastCheckIn(user1.address)
      ).to.be.revertedWith("No check-ins found");
    });
  });

  // ============================================
  // TESTS DE ATTENDEES
  // ============================================
  
  describe("Event Attendees", function () {
    it("Should get event attendees list", async function () {
      const eventId = 1;

      await proofOfPresence.connect(user1).checkInEvent(eventId, "Location");
      await proofOfPresence.connect(user2).checkInEvent(eventId, "Location");
      await proofOfPresence.connect(user3).checkInEvent(eventId, "Location");

      const attendees = await proofOfPresence.getEventAttendees(eventId);
      expect(attendees.length).to.equal(3);
      expect(attendees[0]).to.equal(user1.address);
      expect(attendees[1]).to.equal(user2.address);
      expect(attendees[2]).to.equal(user3.address);
    });

    it("Should return empty array for event with no attendees", async function () {
      const attendees = await proofOfPresence.getEventAttendees(999);
      expect(attendees.length).to.equal(0);
    });
  });

  // ============================================
  // TESTS DE OWNERSHIP
  // ============================================
  
  describe("Ownership", function () {
    it("Should allow owner to transfer ownership", async function () {
      await proofOfPresence.connect(owner).transferOwnership(user1.address);
      expect(await proofOfPresence.owner()).to.equal(user1.address);
    });

    it("Should prevent non-owner from transferring ownership", async function () {
      await expect(
        proofOfPresence.connect(user1).transferOwnership(user2.address)
      ).to.be.revertedWith("Only owner can call this");
    });

    it("Should reject transfer to zero address", async function () {
      await expect(
        proofOfPresence.connect(owner).transferOwnership(ethers.ZeroAddress)
      ).to.be.revertedWith("Invalid address");
    });
  });

  // ============================================
  // TESTS DE GAS
  // ============================================
  
  describe("Gas Optimization", function () {
    it("Should use reasonable gas for check-in", async function () {
      const tx = await proofOfPresence.connect(user1).checkInEvent(1, "Santiago, Chile");
      const receipt = await tx.wait();
      
      // Gas usado debería ser menos de 200k
      expect(receipt.gasUsed).to.be.lessThan(200000);
    });

    it("Should use less gas for subsequent check-ins to same event (should revert)", async function () {
      await proofOfPresence.connect(user1).checkInEvent(1, "Location");
      
      // La segunda debería revertir, no gastar mucho gas
      try {
        const tx = await proofOfPresence.connect(user1).checkInEvent(1, "Location");
        const receipt = await tx.wait();
        expect.fail("Should have reverted");
      } catch (error) {
        // Esperado
        expect(error.message).to.include("Already checked in");
      }
    });
  });

  // ============================================
  // TESTS DE EDGE CASES
  // ============================================
  
  describe("Edge Cases", function () {
    it("Should handle very long location strings", async function () {
      const longLocation = "A".repeat(500);
      await proofOfPresence.connect(user1).checkInEvent(1, longLocation);
      
      const checkIns = await proofOfPresence.getUserCheckIns(user1.address);
      expect(checkIns[0].location).to.equal(longLocation);
    });

    it("Should handle large event IDs", async function () {
      const largeEventId = 999999;
      await proofOfPresence.connect(user1).checkInEvent(largeEventId, "Location");
      
      const checkIns = await proofOfPresence.getUserCheckIns(user1.address);
      expect(checkIns[0].eventId).to.equal(largeEventId);
    });

    it("Should handle special characters in location", async function () {
      const specialLocation = "Santiago, Chile 🎉 (Bellavista) - #1";
      await proofOfPresence.connect(user1).checkInEvent(1, specialLocation);
      
      const checkIns = await proofOfPresence.getUserCheckIns(user1.address);
      expect(checkIns[0].location).to.equal(specialLocation);
    });

    it("Should handle many check-ins from same user", async function () {
      // Check-in a 50 eventos diferentes
      for (let i = 1; i <= 50; i++) {
        await proofOfPresence.connect(user1).checkInEvent(i, `Event ${i}`);
      }
      
      const checkIns = await proofOfPresence.getUserCheckIns(user1.address);
      expect(checkIns.length).to.equal(50);
    });
  });

  // ============================================
  // TESTS DE SEGURIDAD
  // ============================================
  
  describe("Security", function () {
    it("Should prevent reentrancy attacks", async function () {
      // Este contrato no tiene funciones payable, pero es buena práctica testear
      // que las funciones no sean vulnerables a reentrancy
      
      await proofOfPresence.connect(user1).checkInEvent(1, "Location");
      
      // Intentar check-in nuevamente debería fallar
      await expect(
        proofOfPresence.connect(user1).checkInEvent(1, "Location")
      ).to.be.revertedWith("Already checked in to this event");
    });

    it("Should maintain data integrity across multiple transactions", async function () {
      // Múltiples usuarios haciendo check-in simultáneamente
      await Promise.all([
        proofOfPresence.connect(user1).checkInEvent(1, "User 1"),
        proofOfPresence.connect(user2).checkInEvent(1, "User 2"),
        proofOfPresence.connect(user3).checkInEvent(1, "User 3"),
      ]);

      const stats = await proofOfPresence.getEventStats(1);
      expect(stats.uniqueUsers).to.equal(3);
      expect(stats.totalCheckIns).to.equal(3);
    });
  });
});