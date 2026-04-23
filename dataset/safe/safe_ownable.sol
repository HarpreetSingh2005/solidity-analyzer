// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeOwnable {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    function changeOwner(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Zero address");
        owner = newOwner;
    }

    function withdraw() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}