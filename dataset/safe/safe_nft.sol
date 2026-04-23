// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeNFT {
    mapping(uint256 => address) public ownerOf;
    uint256 public totalSupply;

    function mint() public {
        totalSupply++;
        ownerOf[totalSupply] = msg.sender;
    }

    function transfer(uint256 tokenId, address to) public {
        require(ownerOf[tokenId] == msg.sender, "Not owner");
        ownerOf[tokenId] = to;
    }
}