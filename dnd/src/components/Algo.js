"use client"

import React from 'react'
import image0001 from '../assets/0001.jpg';
import image0002 from '../assets/0002.jpg';
import image0003 from '../assets/0003.jpg';
import image0004 from '../assets/0004.jpg';
import image0005 from '../assets/0005.jpg';
import image0006 from '../assets/0006.jpg';
import image0007 from '../assets/0007.jpg';
import image0008 from '../assets/0008.jpg';
import image0009 from '../assets/0009.jpg';
import image0010 from '../assets/0010.jpg';
import image0011 from '../assets/0011.jpg';
import image0012 from '../assets/0012.jpg';
import image0013 from '../assets/0013.jpg';


const images = [
  image0001,
  image0002,
  image0003,
  image0004,
  image0005,
  image0006,
  image0007,
  image0008,
  image0009,
  image0010,
  image0011,
  image0012,
  image0013,
];


// for (let i = 1; i <= 13; i++) {
//   const paddedIndex = i.toString().padStart(4, '0'); // Pad index with zeros
//   const imagePath = `../../assets/${paddedIndex}.jpg`;
//   const imageImport = require(imagePath) // Replace with actual path
//   imagePaths.push(imagePath);
// }

function Algo() {


  return (
    <div className='pl-12 w-full flex h-max'>
    <div className='w-full mt-10 h-full flex flex-col space-y-10'>
      <div className='flex gap-4 items-center'>
        <svg xmlns="http://www.w3.org/2000/svg" width="8" height="14" viewBox="0 0 8 14" fill="none">
          <path d="M6 2L2 7L6 12" stroke="black" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <p className='text-xl font-bold'>Know All About D&D Algorithm</p>
      </div>

      <div className='w-full pr-12 flex-col '>
      <ul className='space-y-10'>
        {images.map((image, index) => (
          <li key={index}>
            <img src={image.src} alt={`Image${index + 1}.src`} />
          </li>
        ))}
      </ul>
</div>
    </div>
  </div>
  )
}

export default Algo