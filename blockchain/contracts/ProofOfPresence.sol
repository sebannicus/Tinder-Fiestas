// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ProofOfPresence {
    struct CheckIn {
        address user;
        string location;
        uint256 timestamp;
        uint256 eventId;
    }

    event EventCheckedIn(
        address indexed user,
        uint256 indexed eventId,
        string location,
        uint256 timestamp
    );

    mapping(address => CheckIn[]) public userCheckIns;

    function checkInEvent(uint256 _eventId, string memory _location) public {
        CheckIn memory newCheckIn = CheckIn({
            user: msg.sender,
            location: _location,
            timestamp: block.timestamp,
            eventId: _eventId
        });

        userCheckIns[msg.sender].push(newCheckIn);

        emit EventCheckedIn(msg.sender, _eventId, _location, block.timestamp);
    }

    function getUserCheckIns(address _user) public view returns (CheckIn[] memory) {
        return userCheckIns[_user];
    }
}
