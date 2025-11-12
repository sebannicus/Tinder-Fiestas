// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract ProofOfPresence {
    struct CheckIn {
        address user;
        string location;
        uint256 timestamp;
        uint256 eventId;
    }

    // 🔹 Mapeo principal: wallet → lista de check-ins
    mapping(address => CheckIn[]) public userCheckIns;

    // 🔹 Evento global emitido cada vez que alguien asiste
    event EventCheckedIn(address indexed user, uint256 indexed eventId, string location, uint256 timestamp);

    // ✅ Registrar check-in general (sin evento específico)
    function checkIn(string memory _location) public {
        CheckIn memory newCheckIn = CheckIn({
            user: msg.sender,
            location: _location,
            timestamp: block.timestamp,
            eventId: 0
        });

        userCheckIns[msg.sender].push(newCheckIn);

        emit EventCheckedIn(msg.sender, 0, _location, block.timestamp);
    }

    // ✅ Registrar asistencia a un evento específico
    function checkInEvent(uint256 _eventId, string memory _location) public {
        require(_eventId > 0, "Evento no valido");

        CheckIn memory newCheckIn = CheckIn({
            user: msg.sender,
            location: _location,
            timestamp: block.timestamp,
            eventId: _eventId
        });

        userCheckIns[msg.sender].push(newCheckIn);

        emit EventCheckedIn(msg.sender, _eventId, _location, block.timestamp);
    }

    // ✅ Obtener historial de un usuario
    function getUserCheckIns(address _user) public view returns (CheckIn[] memory) {
        return userCheckIns[_user];
    }
}
