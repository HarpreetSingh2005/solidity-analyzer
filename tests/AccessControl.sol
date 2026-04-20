// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AccessControl {
    address public owner;
    uint256 public data;

    constructor() {
        owner = msg.sender;
    }

    // Vulnerable: Anyone can change the owner
    function changeOwner(address _newOwner) public {
        owner = _newOwner;
    }

    // Vulnerable: Anyone can change sensitive data
    function setSensitiveData(uint256 _data) public {
        data = _data;
    }
}
