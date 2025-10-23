// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ProofOfPresence {
    event CheckIn(address indexed user, string location);

    mapping(address => string) public lastCheckIn;

    function checkIn(string memory _location) public {
        lastCheckIn[msg.sender] = _location;
        emit CheckIn(msg.sender, _location);
    }

    function getLastLocation(address _user) public view returns (string memory) {
        return lastCheckIn[_user];
    }
}
