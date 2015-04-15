import pdb
from scrapy_balloons.utils.allfunctions import *
from scrapy.shell import inspect_response
import re
from scrapy import Selector

class cmivfx:
    courses_categories_url = "https://cmivfx.com/tutorial/getByCategoryId/%s"
    detail_course_url = "https://cmivfx.com/tutorial/getDetails"
    tutorial_info = "https://cmivfx.com/template/module/tutorialInfo"
    courses_detail = {}
    courses_handled_number = 0

    """
    Step 1: get all categories ids
    Step 2: get course detail for each course and put in cache
    Step 3: get tutorial info for each course, get course detail from cache and build the output json.
    """

    @classmethod
    def start(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        # step 1 : get all categories ids
        categories_id = response.xpath("//section[@data-category]/@data-category").extract()
        categories_filter_ids = []
        for id in categories_id:
            try:
                categories_filter_ids.append(int(id))
            except:
                pass
        categories_filter_ids = categories_filter_ids if  balloon_spider.limit == -1 else categories_filter_ids[:balloon_spider.limit]
        for id in categories_filter_ids:
            yield Request(url=cmivfx.courses_categories_url % (id), headers={'X-Requested-With': 'XMLHttpRequest'},
                          callback=cmivfx.parse_category)


    @classmethod
    def parse_category(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        # see modal 1
        data = json.loads(response.body)
        courses_ids = [course_info['id'] for course_info in data]
        # step 2 : get all courses ids
        if balloon_spider.limit != -1 and cmivfx.courses_handled_number > balloon_spider.limit:
            yield None
        else:
            cmivfx.courses_handled_number += len(courses_ids)
            # make request for course
            for id in courses_ids:
                yield FormRequest(url=cmivfx.detail_course_url, headers={'X-Requested-With': 'XMLHttpRequest'},
                                  callback=cmivfx.parse_course_detail
                                  , formdata={'tutId': id}, dont_filter=True)

    @classmethod
    def parse_course_detail(cls, response):
        # see modal 2
        data = json.loads(response.body)
        course_id = data['id']
        cmivfx.courses_detail[course_id] = data
        #make request for tutorialInfo
        return FormRequest(url=cmivfx.tutorial_info, headers={'X-Requested-With': 'XMLHttpRequest'},
                           callback=cmivfx.parse_tutorial_info, formdata={'tutId': course_id}, dont_filter=True,
                           meta={'course_id': course_id}
        )


    @classmethod
    def parse_tutorial_info(cls, response):
        from scrapy_balloons.spiders.balloon import balloon_spider
        from scrapy import Selector
        course_id = response.meta['course_id']
        course_detail = cmivfx.courses_detail[course_id]
        product = balloon_spider.create_new_product()
        #build product
        product['name'] = course_detail['name']
        product['product_url'] = urljoin('https://cmivfx.com/store/', course_detail['id'])
        product['partner_prod_id'] = course_detail['id']
        product['product_image_url'] = course_detail['image_large']
        product['description'] = course_detail['longDescription']
        product['toc'] = re.sub('Chapter Descriptions', '', course_detail['marketingText'])
        product['published_date'] = course_detail['releaseDate']
        product['duration_display'] = re.sub('\\.', ':', course_detail['videoDuration'])
        product['duration_filter'] = duration_filter(re.sub('\\.', ':', course_detail['videoDuration']))
        product['price_display_float'] = course_detail['price']
        return product



# modal 1 : category
#[{"id":"584","name":"Nuke-Mari Workflows","price":"49.95","releaseDate":"2014-03-13 00:00:00","image_thumb":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/small\\/match-moving-and-more-in-nuke,-maya-and-mari-thumb.jpg","image_medium":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/medium\\/match-moving-and-more-in-nuke,-maya-and-mari-large.jpg","image_large":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/large\\/match-moving-and-more-in-nuke,-maya-and-mari-large.jpg","shortDescription":"Salah Soltane teaches you match moving in Nuke, modeling in Maya, painting in Mari, and even final c...","category":"3D Matchmoving","categoryId":"20"},{"id":"508","name":"Mocha Pro Advanced","price":"19.95","releaseDate":"2012-11-25 00:00:00","image_thumb":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/small\\/1353861765_Master_icon.jpg","image_medium":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/medium\\/1353861765_Master.jpg","image_large":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/large\\/1353861765_Master.jpg","shortDescription":"Brilliant video for advanced match moving scenarios otherwise impossible in other apps. MochaPro dem...","category":"3D Matchmoving","categoryId":"20"},{"id":"309","name":"Motion Control   3D Camera","price":"59.95","releaseDate":"2011-07-05 00:00:00","image_thumb":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/small\\/1309885456_Capturing_04_Master_Icon.jpg","image_medium":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/medium\\/1309885456_Capturing_04_Master_Image.jpg","image_large":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/large\\/1309885456_Capturing_04_Master_Image.png","shortDescription":"Learn how to use Motion Control camera data, from entry level skills to more advanced data extractio...","category":"3D Matchmoving","categoryId":"20"},{"id":"301","name":"Camera Based Motion Capture","price":"59.95","releaseDate":"2011-05-26 00:00:00","image_thumb":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/small\\/1306416932_Master_Thumb.jpg","image_medium":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/medium\\/1306416932_Master.jpg","image_large":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/large\\/1306416932_Master.jpg","shortDescription":"This video shows Motion Capture Tracking with Matchmover and 3DSMax Character Studio. However, it ca...","category":"3D Matchmoving","categoryId":"20"},{"id":"242","name":"Complete Syntheyes Training","price":"49.95","releaseDate":"2011-02-15 00:00:00","image_thumb":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/small\\/242-Thumb_Large.jpg","image_medium":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/medium\\/42f216de-0c66-4cc1-b699-1ab601b1d0c4.jpg","image_large":"https:\\/\\/cmivfx.com\\/img\\/tutorial\\/large\\/42f216de-0c66-4cc1-b699-1ab601b1d0c4.jpg","shortDescription":"This is the most complete Syntheyes training on the market, and you better believe its a cmiVFX vide...","category":"3D Matchmoving","categoryId":"20"}]

# modal 2 : course detail
# {"marketingText":"<h3>Chapter Descriptions<\/h3>\n<h4>Introduction<\/h4>\n<p>\nFor starters we&#39;ll use a simple shot and do the most obvious thing when you first open Syntheyes: A completely automatic track. In a matter of literally seconds you&#39;ll have a pretty usable result, that will quickly improve by using some simple clean-up techniques. Orient the scene in 3d-space and insert 3D-objects into your scene to test if everything works, export your camera-solution and voil\u00e1 - you have a decent matchmove in just a few minutes.\n<\/p>\t\n<h4>Solving a shaky handheld shot<\/h4>\n<p>\nLife not often makes it easy for you, and so you&#39;ll often be confronted with things like motion-blur, camera-shake and lens-distortion. So for the more difficult shots we&#39;ll have to bring the big guns in. Automatic tracker cleanup, manual control over each tracker-curve in the graphs-editor and fine-tune trackers can really improve your camera solution. To solve fast and shaky hand-held footage with lots of motion-blur it&#39;s best to use supervised tracking to give you the most control over each tracker. If you&#39;re footage was shot with a lens that has barrel-distortion then you have another problem that can make things more complicated. Tracks will have lots of errors, and 3D objects will not fit to the footage not matter what. Luckily Syntheyes has a clever way to get rid of lens-distortion. Or even to re-distort the CGI, if the director wants to work with the original footage later in compositing.\n<\/p>\n<h4>Modeling with Syntheyes<\/h4>\n<p>\nWith the tracking-features and resulting 3d-points you can not only define the camera, but also re-model the scene, just use the points to define a mesh! And if there are not enough features for you to re-create the scene, insert zero weighted trackers (ZWT) that don&#39;t affect the camera solution but will position themselves in the correct place in your 3d environment. And if you need more organic shapes to be rebuilt, add thousands of 3d-points all at once to build your mesh. You can even texture that mesh by using camera-projection right within Syntheyes, to test if camera-mapping will work later in your 3d- or compositing-application.\n<\/p>\t\n<h4>Solving Tripod shots - with 3d environment?<\/h4>\n<p>\nThe common problem with tripod shots is that it is impossible to get any usable 3d information out of just a camera-pan. The solution of the camera movement might be good, still it can be hard to position it in a reasonable and exact way in 3d-space. That problem can quickly be solved with Syntheye&#39;s lens-tools. Use any straight perspective lines in one frame of your tripod-shot to setup a coordinate system that let&#39;s you position objects in your scene more easily - that makes life easier for the 3d-artist! You can even use that method on still images.\n<\/p>\t\n<h4>A moving camera - and a moving object!<\/h4>\n<p>\nAlthough primarily a camera-tracker, Syntheyes does a really good job at object-tracking. The last chapter of this tutorial shows you how to track camera and objects in one scene altogether, how to setup their coordinate systems and how to orient them in 3d-space. You can really do amazing things with this great software. Make sure you have some time and your favorite compositing and 3d application at hand! You&#39;ll want to try out all these goodies immediately!\n<\/p>\t\n<h4>About the Author<\/h4>\n<p>\nSebastian K\u00f6nig is a German 3D-artist who is working as a freelancer and CG-instructor for several years now. During his studies for Education of Art he discovered the joy of modeling and creating 3D-Animations with Blender and hasn&#39;t stopped since.\u00a0 Being a passionate Blender-User he has been teaching Blender at the University of Art and Design Halle\/Germany.\u00a0 He has been working for various studios and companies as a 3D-Artist and freelancer.\u00a0 During the dozens of projects and jobs he completed with Blender he got a profound knowledge of almost every aspect of this great Open-Source 3D-application. Since 2010 he is an official Blender Foundation Certified Trainer.\n<\/p>","longDescription":"Syntheyes, available at http:\/\/www.ssontech.com, is one of the fastest, feature-rich and yet surprisingly inexpensive camera-trackers out there. This tutorial not only gets you started with basic and advanced tracking, but will also dig deeper into the vast feature tool-set of Syntheyes that goes way beyond simple tracking.","activeVideo":"1","activeStore":"1","id":"242","name":"Complete Syntheyes Training","price":"49.95","releaseDate":"2011-02-15 00:00:00","image_thumb":"https:\/\/cmivfx.com\/img\/tutorial\/small\/242-Thumb_Large.jpg","image_medium":"https:\/\/cmivfx.com\/img\/tutorial\/medium\/42f216de-0c66-4cc1-b699-1ab601b1d0c4.jpg","image_large":"https:\/\/cmivfx.com\/img\/tutorial\/large\/42f216de-0c66-4cc1-b699-1ab601b1d0c4.jpg","shortDescription":"This is the most complete Syntheyes training on the market, and you better believe its a cmiVFX vide...","category":"3D Matchmoving","categoryId":"20","videoId":"127","videoDuration":"03.44.19","chapters":[{"id":"474","videoId":"127","name":"Chapter 01","description":"Introduction","timeCode":"12.9166666667"},{"id":"475","videoId":"127","name":"Chapter 02","description":"First Clip","timeCode":"246.833333333"},{"id":"476","videoId":"127","name":"Chapter 03","description":"Load First Shot","timeCode":"360.333333333"},{"id":"477","videoId":"127","name":"Chapter 04","description":"Your First Track","timeCode":"545.75"},{"id":"478","videoId":"127","name":"Chapter 05","description":"Examining The Results","timeCode":"979.333333333"},{"id":"479","videoId":"127","name":"Chapter 06","description":"The RMS Error","timeCode":"1045.58333333"},{"id":"480","videoId":"127","name":"Chapter 07","description":"Search Bad Trackers","timeCode":"1206.58333333"},{"id":"481","videoId":"127","name":"Chapter 08","description":"Clean Up Trackers","timeCode":"1550.83333333"},{"id":"482","videoId":"127","name":"Chapter 09","description":"Test Geometry","timeCode":"2027.83333333"},{"id":"483","videoId":"127","name":"Chapter 10","description":"Export Scene","timeCode":"2512.5"},{"id":"484","videoId":"127","name":"Chapter 11","description":"Open New Shot","timeCode":"2647.66666667"},{"id":"485","videoId":"127","name":"Chapter 12","description":"Graph Editor","timeCode":"3112.58333333"},{"id":"486","videoId":"127","name":"Chapter 13","description":"Solving The Scene","timeCode":"3670.58333333"},{"id":"487","videoId":"127","name":"Chapter 14","description":"Lens Distortion","timeCode":"4075.58333333"},{"id":"488","videoId":"127","name":"Chapter 15","description":"Image Preprocessing","timeCode":"5002.66666667"},{"id":"489","videoId":"127","name":"Chapter 16","description":"Manual Tracking Process","timeCode":"5248"},{"id":"490","videoId":"127","name":"Chapter 17","description":"Constraints","timeCode":"7323.83333333"},{"id":"491","videoId":"127","name":"Chapter 18","description":"Saving Sequences","timeCode":"8880.33333333"},{"id":"492","videoId":"127","name":"Chapter 19","description":"Stabilization","timeCode":"9130"},{"id":"493","videoId":"127","name":"Chapter 20","description":"Nodal Pans","timeCode":"10020"},{"id":"494","videoId":"127","name":"Chapter 21","description":"Object Tracking","timeCode":"11112.5833333"}],"images":[{"id":"216","type":"IMAGE","url":"https:\/\/cmivfx.com\/img\/tutorial\/media\/16f40474-64d9-46b2-832c-f567192c3ebb.jpg"},{"id":"217","type":"IMAGE","url":"https:\/\/cmivfx.com\/img\/tutorial\/media\/85ab0db9-3448-493e-867a-1baa0f492304.jpg"},{"id":"218","type":"IMAGE","url":"https:\/\/cmivfx.com\/img\/tutorial\/media\/d489dec8-4fe8-4ea2-9985-04cccdce06ae.jpg"},{"id":"219","type":"IMAGE","url":"https:\/\/cmivfx.com\/img\/tutorial\/media\/3af72062-37e1-429d-b350-4d2d20acd377.jpg"},{"id":"220","type":"IMAGE","url":"https:\/\/cmivfx.com\/img\/tutorial\/media\/da10c679-b0a1-4b3e-9577-8b688d0a6b24.jpg"}]}