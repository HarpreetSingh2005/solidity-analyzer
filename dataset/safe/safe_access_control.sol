// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeAccessControl {
    address public owner;
    mapping(address => bool) public admins;

    constructor() {
        owner = msg.sender;
        admins[msg.sender] = true;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyAdmin() {
        require(admins[msg.sender], "Not admin");
        _;
    }

    function addAdmin(address newAdmin) public onlyOwner {
        admins[newAdmin] = true;
    }
}